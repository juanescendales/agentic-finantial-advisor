import pytest

from src.graph.schemas import (
    AnalystReport,
    FundamentalsSnapshot,
    MarketSnapshot,
    NewsItem,
)
from src.graph.state import AdvisorState
from src.nodes.analyst import analyst_synthesize


@pytest.mark.integration
def test_analyst_synthesize_returns_populated_report() -> None:
    state = AdvisorState(
        ticker="AAPL",
        company_name="Apple Inc.",
        news_data=[
            NewsItem(
                title="Apple beats Q3 earnings expectations",
                source="Reuters",
                summary="Apple reported stronger than expected iPhone sales and raised guidance.",
            ),
        ],
        fundamentals_data=FundamentalsSnapshot(
            as_of_date="2026-08-01",
            market_cap=3.1e12,
            trailing_pe=35.2,
            revenue_growth=0.08,
            profit_margins=0.27,
        ),
        market_data=MarketSnapshot(
            start_date="2026-02-01",
            end_date="2026-08-01",
            last_close=225.5,
            sma_50=220.1,
            rsi_14=58.3,
            volatility_6m=0.31,
        ),
    )

    result = analyst_synthesize(state)
    report = result["analyst_report"]

    assert isinstance(report, AnalystReport)
    assert report.summary
