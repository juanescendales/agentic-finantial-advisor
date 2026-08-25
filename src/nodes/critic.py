import time
from typing import Literal, cast

from langgraph.graph import END
from openai.types.chat import ChatCompletionMessageParam

from src.graph.schemas import CriticVerdict
from src.graph.state import AdvisorState
from src.observability.logger import log_node_event
from src.prompts.critic import generate_critic_prompt
from src.tools.llm import LLM_MODEL, request_structured

CriticRoute = Literal["fetch_news", "fetch_fundamentals", "fetch_market", "__end__"]
END_ROUTE = cast(Literal["__end__"], END)
MAX_REVISIONS = 2


def _build_messages(state: AdvisorState) -> list[ChatCompletionMessageParam]:
    prompt = generate_critic_prompt(
        ticker=state.ticker,
        company_name=state.company_name or "",
        analyst_report=(
            state.analyst_report.to_str()
            if state.analyst_report
            else "No analyst report available."
        ),
        decision=(
            state.decision.to_str() if state.decision else "No decision available."
        ),
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
        {"role": "user", "content": prompt.critic_prompt},
    ]


def critic_review(state: AdvisorState) -> dict[str, object]:
    """Review the decision against the report and the raw data.

    Args:
        state: Graph state; reads ``analyst_report``, ``decision`` and the
        three data branches.

    Returns:
        Partial state update with ``critic_verdict``, ``critic_feedback`` and
        ``revision_count``, bumped only when a branch is sent back for another pass.
    """
    messages = _build_messages(state)

    start = time.perf_counter()
    verdict, input_tokens, output_tokens = request_structured(messages, CriticVerdict)
    latency_ms = (time.perf_counter() - start) * 1000

    log_node_event(
        "critic_review",
        status="success",
        model=LLM_MODEL,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        revision_count=state.revision_count,
    )

    return {
        "critic_verdict": verdict,
        "critic_feedback": verdict.feedback,
        "revision_count": (
            state.revision_count + 1 if verdict.needs_more else state.revision_count
        ),
    }


def route_after_critic(
    state: AdvisorState,
) -> CriticRoute:
    # revision_count already includes the revision this verdict is asking for, so the
    # cap is exceeded only past MAX_REVISIONS, not at it.
    if state.revision_count > MAX_REVISIONS:
        return END_ROUTE

    verdict = state.critic_verdict
    if verdict is None or verdict.status == "ok" or verdict.needs_more is None:
        return END_ROUTE

    if verdict.needs_more == "news":
        return "fetch_news"
    if verdict.needs_more == "fundamentals":
        return "fetch_fundamentals"
    return "fetch_market"
