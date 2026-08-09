import time

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.shared_params import ResponseFormatJSONSchema
from pydantic import ValidationError

from src.config import settings
from src.graph.schemas import AnalystReport
from src.graph.state import AdvisorState
from src.observability.logger import log_node_event
from src.prompts.analyst import generate_analyst_prompt

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
LLM_MODEL = "openai/gpt-oss-20b:free"
MAX_ATTEMPTS = 3
_client: OpenAI | None = None


def load_client() -> OpenAI:
    """Load the OpenAI client with the API key from the environment."""
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.open_router_api_key, base_url=OPENROUTER_BASE_URL)
    return _client


def _build_messages(state: AdvisorState) -> list[ChatCompletionMessageParam]:
    prompt = generate_analyst_prompt(
        ticker=state.ticker,
        company_name=state.company_name or "",
        news_data=str([item.to_str() for item in state.news_data]) if state.news_data else "No news data available.",
        fundamentals_data=state.fundamentals_data.to_str() if state.fundamentals_data else "No fundamentals data available.",
        market_data=state.market_data.to_str() if state.market_data else "No market data available.",
    )
    return [
        {"role": "system", "content": prompt.system_prompt},
        {"role": "user", "content": prompt.analyst_prompt},
    ]


def _request_analyst_report(
    client: OpenAI, messages: list[ChatCompletionMessageParam]
) -> tuple[AnalystReport, int, int]:
    """Call the LLM with a schema-constrained response, retrying on validation errors.

    Returns:
        The parsed report and the accumulated (input_tokens, output_tokens) across attempts.
    """
    response_format: ResponseFormatJSONSchema = {
        "type": "json_schema",
        "json_schema": {
            "name": "analyst_report",
            "schema": AnalystReport.model_json_schema(),
        },
    }
    total_input_tokens = 0
    total_output_tokens = 0

    for attempt in range(MAX_ATTEMPTS):
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            response_format=response_format,
        )
        if response.usage:
            total_input_tokens += response.usage.prompt_tokens
            total_output_tokens += response.usage.completion_tokens

        raw_report = response.choices[0].message.content
        if raw_report is None:
            raise ValueError("LLM response content was empty")
        try:
            return AnalystReport.model_validate_json(raw_report), total_input_tokens, total_output_tokens
        except ValidationError as exc:
            if attempt == MAX_ATTEMPTS - 1:
                raise
            messages.append({"role": "assistant", "content": raw_report})
            messages.append(
                {
                    "role": "user",
                    "content": f"Your response did not match the required schema: {exc}. Please resend a corrected JSON object.",
                }
            )

    raise AssertionError("unreachable: loop always returns or raises")


def analyst_synthesize(state: AdvisorState) -> dict[str, AnalystReport]:
    """Synthesize the analyst report from the fetched data.

    Args:
        state: Graph state; reads ``news_data``, ``fundamentals_data``,
        and ``market_data``.

    Returns:
        Partial state update with ``analyst_report``.
    """
    client = load_client()
    messages = _build_messages(state)

    start = time.perf_counter()
    analyst_report, input_tokens, output_tokens = _request_analyst_report(client, messages)
    latency_ms = (time.perf_counter() - start) * 1000

    log_node_event(
        "analyst_synthesize",
        status="success",
        model=LLM_MODEL,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        revision_count=state.revision_count,
    )

    return {"analyst_report": analyst_report}



