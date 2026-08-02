from typing import Literal

from pydantic import BaseModel, Field


class NewsItem(BaseModel):
    title: str
    source: str
    url: str | None = None
    published_at: str | None = None
    summary: str | None = None

    def to_str(self) -> str:
        """Return a string representation of the news item."""
        return f"{self.title} ({self.source}) - body: {self.summary or 'No summary available.'}"


class FundamentalsSnapshot(BaseModel):
    as_of_date: str
    market_cap: float | None = None  # company size: share price x shares outstanding
    trailing_pe: float | None = None  # valuation: price paid per $1 of past earnings
    revenue_growth: float | None = None  # growth: is the business expanding its sales
    profit_margins: float | None = None  # profitability: revenue kept as profit

    def to_str(self) -> str:
        """Return a string representation of the fundamentals snapshot."""
        return (
            f"As of {self.as_of_date} - "
            f"market cap: {self.market_cap if self.market_cap is not None else 'N/A'}, "
            f"trailing P/E: {self.trailing_pe if self.trailing_pe is not None else 'N/A'}, "
            f"revenue growth: {self.revenue_growth if self.revenue_growth is not None else 'N/A'}, "
            f"profit margins: {self.profit_margins if self.profit_margins is not None else 'N/A'}"
        )


class MarketSnapshot(BaseModel):
    start_date: str
    end_date: str
    last_close: float | None = None  # most recent closing price
    sma_50: float | None = None  # trend: 50-day average price
    rsi_14: float | None = None  # momentum: 0-100, >70 overbought, <30 oversold
    volatility_6m: float | None = None  # risk: annualized std of daily returns

    def to_str(self) -> str:
        """Return a string representation of the market snapshot."""
        return (
            f"From {self.start_date} to {self.end_date} - "
            f"last close: {self.last_close if self.last_close is not None else 'N/A'}, "
            f"50-day SMA: {self.sma_50 if self.sma_50 is not None else 'N/A'}, "
            f"14-day RSI: {self.rsi_14 if self.rsi_14 is not None else 'N/A'}, "
            f"6-month volatility: {self.volatility_6m if self.volatility_6m is not None else 'N/A'}"
        )


class AnalystReport(BaseModel):
    summary: str
    bull_case: list[str] = Field(default_factory=list)
    bear_case: list[str] = Field(default_factory=list)
    notable_signals: list[str] = Field(default_factory=list)
    data_quality_flags: list[str] = Field(default_factory=list)


class AdvisorDecision(BaseModel):
    action: Literal["BUY", "HOLD", "SELL"]
    confidence: float = Field(ge=0.0, le=1.0)
    time_horizon: Literal["short", "medium", "long"]
    key_drivers: list[str] = Field(min_length=1)
    reasoning: str


class CriticVerdict(BaseModel):
    status: Literal["ok", "needs_more"]
    confidence_in_decision: float = Field(ge=0.0, le=1.0)
    needs_more: Literal["news", "fundamentals", "market"] | None = None
    feedback: str
