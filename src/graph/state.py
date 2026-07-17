import operator
from typing import Annotated

from pydantic import BaseModel, Field

from src.graph.schemas import (
    AdvisorDecision,
    AnalystReport,
    CriticVerdict,
    FundamentalsSnapshot,
    MarketSnapshot,
    NewsItem,
)


class AdvisorState(BaseModel):
    ticker: str
    company_name: str | None = None
    news_data: list[NewsItem] | None = None
    fundamentals_data: FundamentalsSnapshot | None = None
    market_data: MarketSnapshot | None = None
    analyst_report: AnalystReport | None = None
    decision: AdvisorDecision | None = None
    critic_verdict: CriticVerdict | None = None
    critic_feedback: str | None = None
    revision_count: int = 0
    errors: Annotated[list[str], operator.add] = Field(default_factory=list)
