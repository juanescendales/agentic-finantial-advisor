from typing import Literal

from pydantic import BaseModel, Field


class NewsItem(BaseModel):
    title: str
    source: str
    url: str | None = None
    published_at: str | None = None
    summary: str | None = None


class FundamentalsSnapshot(BaseModel):
    as_of_date: str
    market_cap: float | None = None  # company size: share price x shares outstanding
    trailing_pe: float | None = None  # valuation: price paid per $1 of past earnings
    revenue_growth: float | None = None  # growth: is the business expanding its sales
    profit_margins: float | None = None  # profitability: revenue kept as profit


class MarketSnapshot(BaseModel):
    start_date: str
    end_date: str
    last_close: float | None = None  # most recent closing price
    sma_50: float | None = None  # trend: 50-day average price
    rsi_14: float | None = None  # momentum: 0-100, >70 overbought, <30 oversold
    volatility_6m: float | None = None  # risk: annualized std of daily returns


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
