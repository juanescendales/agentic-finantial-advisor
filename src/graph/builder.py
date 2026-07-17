from typing import Any

from langgraph.graph import END, START, StateGraph

from src.graph.state import AdvisorState
from src.nodes.advisor import advisor_decide
from src.nodes.analyst import analyst_synthesize
from src.nodes.critic import critic_review, route_after_critic
from src.nodes.fetchers import fetch_fundamentals, fetch_market, fetch_news
from src.nodes.validator import route_after_validation, validate_ticker


def build_graph() -> Any:
    graph = StateGraph(AdvisorState)

    graph.add_node("validate_ticker", validate_ticker)
    graph.add_node("fetch_news", fetch_news)
    graph.add_node("fetch_fundamentals", fetch_fundamentals)
    graph.add_node("fetch_market", fetch_market)
    graph.add_node("analyst_synthesize", analyst_synthesize)
    graph.add_node("advisor_decide", advisor_decide)
    graph.add_node("critic_review", critic_review)

    graph.add_edge(START, "validate_ticker")
    graph.add_conditional_edges(
        "validate_ticker",
        route_after_validation,
        ["fetch_news", "fetch_fundamentals", "fetch_market", END],
    )
    graph.add_edge("fetch_news", "analyst_synthesize")
    graph.add_edge("fetch_fundamentals", "analyst_synthesize")
    graph.add_edge("fetch_market", "analyst_synthesize")
    graph.add_edge("analyst_synthesize", "advisor_decide")
    graph.add_edge("advisor_decide", "critic_review")
    graph.add_conditional_edges(
        "critic_review",
        route_after_critic,
        {
            "fetch_news": "fetch_news",
            "fetch_fundamentals": "fetch_fundamentals",
            "fetch_market": "fetch_market",
            END: END,
        },
    )

    return graph.compile()
