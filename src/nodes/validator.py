from typing import Literal, cast

from langgraph.graph import END

from src.graph.state import AdvisorState

ValidationRoute = Literal[
    "fetch_news", "fetch_fundamentals", "fetch_market", "__end__"
]
END_ROUTE = cast(Literal["__end__"], END)


def validate_ticker(state: AdvisorState) -> dict[str, object]:
    raise NotImplementedError("validate_ticker must validate ticker and set company_name or errors.")


def route_after_validation(state: AdvisorState) -> list[ValidationRoute] | Literal["__end__"]:
    if state.errors:
        return END_ROUTE
    routes: list[ValidationRoute] = ["fetch_news", "fetch_fundamentals", "fetch_market"]
    return routes
