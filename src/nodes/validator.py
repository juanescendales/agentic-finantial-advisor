from typing import Literal, cast

import yfinance as yf
from langgraph.graph import END

from src.graph.state import AdvisorState

ValidationRoute = Literal[
    "fetch_news", "fetch_fundamentals", "fetch_market", "__end__"
]
END_ROUTE = cast(Literal["__end__"], END)


def validate_ticker(state: AdvisorState) -> dict[str, object]:
    try:
        info = yf.Ticker(state.ticker).info
    except Exception as exc:
        return {"errors": [f"Failed to validate ticker '{state.ticker}': {exc}"]}

    symbol = info.get("symbol")
    quote_type = info.get("quoteType")
    if not symbol or not quote_type:
        return {"errors": [f"Ticker '{state.ticker}' not found"]}

    return {"company_name": info.get("longName") or info.get("shortName") or symbol}


def route_after_validation(state: AdvisorState) -> list[ValidationRoute] | Literal["__end__"]:
    if state.errors:
        return END_ROUTE
    routes: list[ValidationRoute] = ["fetch_news", "fetch_fundamentals", "fetch_market"]
    return routes
