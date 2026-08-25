import pytest

from src.graph.schemas import (
    AdvisorDecision,
    AnalystReport,
    CriticVerdict,
    FundamentalsSnapshot,
    MarketSnapshot,
    NewsItem,
)
from src.graph.state import AdvisorState
from src.nodes.critic import critic_review


@pytest.mark.integration
def test_critic_review_returns_a_verdict() -> None:
    state = AdvisorState(
        ticker="AAPL",
        company_name="Apple Inc.",
        news_data=[
            NewsItem(
                title="Apple beats Q3 earnings expectations",
                source="reuters.com",
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
        analyst_report=AnalystReport(
            summary="Services growth offsets hardware softness.",
            bull_case=["Services revenue grew 14% year over year"],
            bear_case=["iPhone sales in China declined"],
            notable_signals=["Price above the 50-day SMA"],
        ),
        decision=AdvisorDecision(
            action="BUY",
            confidence=0.72,
            time_horizon="medium",
            key_drivers=["Services growth", "Earnings beat"],
            reasoning="Services momentum and the guidance raise outweigh the China weakness.",
        ),
    )

    result = critic_review(state)
    verdict = result["critic_verdict"]

    assert isinstance(verdict, CriticVerdict)
    assert verdict.feedback
    assert result["critic_feedback"] == verdict.feedback
    expected_count = 1 if verdict.needs_more else 0
    assert result["revision_count"] == expected_count


@pytest.mark.integration
def test_critic_review_flags_the_missing_branch() -> None:
    """A decision resting on news claims with no news data should send news back."""
    state = AdvisorState(
        ticker="AAPL",
        company_name="Apple Inc.",
        fundamentals_data=FundamentalsSnapshot(
            as_of_date="2026-08-01", market_cap=3.1e12, trailing_pe=35.2
        ),
        market_data=MarketSnapshot(
            start_date="2026-02-01",
            end_date="2026-08-01",
            last_close=225.5,
            rsi_14=58.3,
        ),
        analyst_report=AnalystReport(
            summary="Apple looks strong.",
            bull_case=["Recent product launch was well received"],
            data_quality_flags=["no news coverage available"],
        ),
        decision=AdvisorDecision(
            action="BUY",
            confidence=0.9,
            time_horizon="short",
            key_drivers=["Product launch reception", "Positive press coverage"],
            reasoning="Recent coverage of the launch has been overwhelmingly positive.",
        ),
    )

    verdict = critic_review(state)["critic_verdict"]

    assert isinstance(verdict, CriticVerdict)
    assert verdict.status == "needs_more"
    assert verdict.needs_more == "news"
