from typing import Literal, cast

from langgraph.graph import END

from src.graph.state import AdvisorState

CriticRoute = Literal["fetch_news", "fetch_fundamentals", "fetch_market", "__end__"]
END_ROUTE = cast(Literal["__end__"], END)


def critic_review(state: AdvisorState) -> dict[str, object]:
    raise NotImplementedError("critic_review must populate critic_verdict.")


def route_after_critic(
    state: AdvisorState,
) -> CriticRoute:
    if state.revision_count >= 2:
        return END_ROUTE

    verdict = state.critic_verdict
    if verdict is None or verdict.status == "ok" or verdict.needs_more is None:
        return END_ROUTE

    if verdict.needs_more == "news":
        return "fetch_news"
    if verdict.needs_more == "fundamentals":
        return "fetch_fundamentals"
    return "fetch_market"
