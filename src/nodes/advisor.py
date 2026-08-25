import time

from openai.types.chat import ChatCompletionMessageParam

from src.graph.schemas import AdvisorDecision
from src.graph.state import AdvisorState
from src.observability.logger import log_node_event
from src.prompts.advisor import generate_advisor_prompt
from src.tools.llm import LLM_MODEL, request_structured


def _build_messages(state: AdvisorState) -> list[ChatCompletionMessageParam]:
    prompt = generate_advisor_prompt(
        ticker=state.ticker,
        company_name=state.company_name or "",
        analyst_report=(
            state.analyst_report.to_str()
            if state.analyst_report
            else "No analyst report available."
        ),
    )
    return [
        {"role": "system", "content": prompt.system_prompt},
        {"role": "user", "content": prompt.advisor_prompt},
    ]


def advisor_decide(state: AdvisorState) -> dict[str, AdvisorDecision]:
    """Decide an action from the analyst report.

    Args:
        state: Graph state; reads ``analyst_report``.

    Returns:
        Partial state update with ``decision``.
    """
    messages = _build_messages(state)

    start = time.perf_counter()
    decision, input_tokens, output_tokens = request_structured(
        messages, AdvisorDecision
    )
    latency_ms = (time.perf_counter() - start) * 1000

    log_node_event(
        "advisor_decide",
        status="success",
        model=LLM_MODEL,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        revision_count=state.revision_count,
    )

    return {"decision": decision}
