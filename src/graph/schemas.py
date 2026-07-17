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
    market_cap: float | None = None
    trailing_pe: float | None = None
    revenue_growth: float | None = None
    profit_margins: float | None = None


class MarketSnapshot(BaseModel):
    start_date: str
    end_date: str
    last_close: float | None = None
    sma_50: float | None = None
    rsi_14: float | None = None
    volatility_6m: float | None = None


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
