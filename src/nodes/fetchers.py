from datetime import datetime

import pandas as pd
import yfinance as yf

from src.graph.schemas import FundamentalsSnapshot, MarketSnapshot
from src.graph.state import AdvisorState


def compute_rsi(close: pd.Series, window: int = 14) -> pd.Series:
    """Relative Strength Index using Wilder's smoothing.

    Wilder smooths average gains/losses with an EMA of ``alpha = 1/window``
    (``adjust=False`` gives the recursive form), which decays old data smoothly
    instead of dropping it abruptly like a simple rolling mean would.
    """
    delta = close.diff()
    gains = delta.clip(lower=0)  # negative changes set to 0
    losses = -delta.clip(upper=0)  # positive changes set to 0, kept positive
    avg_gain = gains.ewm(alpha=1 / window, adjust=False).mean()
    avg_loss = losses.ewm(alpha=1 / window, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100 - 100 / (1 + rs)


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
    """Fetch market data: how is the stock's price behaving?

    Market data describes price action from historical prices (trend, momentum,
    volatility), independent of the company's underlying financials.

    Args:
        state: Graph state; reads ``ticker``.

    Returns:
        Partial state update with ``market_data``.
    """
    company_hist = yf.Ticker(state.ticker).history(period="6mo")
    close = company_hist["Close"]

    market_snapshot = MarketSnapshot(
        start_date=company_hist.index[0].strftime("%Y-%m-%d"),
        end_date=company_hist.index[-1].strftime("%Y-%m-%d"),
        last_close=float(close.iloc[-1]),
        sma_50=float(close.rolling(window=50).mean().iloc[-1]),
        rsi_14=float(compute_rsi(close, window=14).iloc[-1]),
        volatility_6m=float(close.pct_change().std() * (252**0.5)),  # annualized
    )

    return {"market_data": market_snapshot}
