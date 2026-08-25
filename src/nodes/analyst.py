import time

from openai.types.chat import ChatCompletionMessageParam

from src.graph.schemas import AnalystReport
from src.graph.state import AdvisorState
from src.observability.logger import log_node_event
from src.prompts.analyst import generate_analyst_prompt
from src.tools.llm import LLM_MODEL, request_structured


def _build_messages(state: AdvisorState) -> list[ChatCompletionMessageParam]:
    prompt = generate_analyst_prompt(
        ticker=state.ticker,
        company_name=state.company_name or "",
        news_data=(
            str([item.to_str() for item in state.news_data])
            if state.news_data
            else "No news data available."
        ),
        fundamentals_data=(
            state.fundamentals_data.to_str()
            if state.fundamentals_data
            else "No fundamentals data available."
        ),
        market_data=(
            state.market_data.to_str()
            if state.market_data
            else "No market data available."
        ),
    )
    return [
        {"role": "system", "content": prompt.system_prompt},
        {"role": "user", "content": prompt.analyst_prompt},
    ]


def analyst_synthesize(state: AdvisorState) -> dict[str, AnalystReport]:
    """Synthesize the analyst report from the fetched data.

    Args:
        state: Graph state; reads ``news_data``, ``fundamentals_data``,
        and ``market_data``.

    Returns:
        Partial state update with ``analyst_report``.
    """
    messages = _build_messages(state)

    start = time.perf_counter()
    analyst_report, input_tokens, output_tokens = request_structured(
        messages, AnalystReport
    )
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
