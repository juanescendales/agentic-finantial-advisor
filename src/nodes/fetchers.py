from datetime import datetime

import yfinance as yf

from src.graph.schemas import FundamentalsSnapshot
from src.graph.state import AdvisorState


def fetch_news(state: AdvisorState) -> dict[str, object]:
    raise NotImplementedError("fetch_news must populate news_data.")


def fetch_fundamentals(state: AdvisorState) -> dict[str, object]:
    """Fetch fundamentals: is this a good business, and is it cheap?

    Fundamentals describe the health of the company itself (valuation, growth,
    profitability) from its financials, independent of its stock price.

    Args:
        state: Graph state; reads ``ticker``.

    Returns:
        Partial state update with ``fundamentals_data``.
    """
    company_info = yf.Ticker(state.ticker).info
    fundamentals_snapshot = FundamentalsSnapshot(
        as_of_date=datetime.now().strftime("%Y-%m-%d"),
        market_cap=company_info.get("marketCap"),
        trailing_pe=company_info.get("trailingPE"),
        revenue_growth=company_info.get("revenueGrowth"),
        profit_margins=company_info.get("profitMargins"),
    )

    return {"fundamentals_data": fundamentals_snapshot}


def fetch_market(state: AdvisorState) -> dict[str, object]:
    raise NotImplementedError("fetch_market must populate market_data.")
