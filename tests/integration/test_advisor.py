import pytest

from src.graph.schemas import AdvisorDecision, AnalystReport
from src.graph.state import AdvisorState
from src.nodes.advisor import advisor_decide


@pytest.mark.integration
def test_advisor_decide_returns_populated_decision() -> None:
    state = AdvisorState(
        ticker="AAPL",
        company_name="Apple Inc.",
        analyst_report=AnalystReport(
            summary="Apple posted a strong quarter with services offsetting hardware softness.",
            bull_case=[
                "Services revenue grew 14% year over year with expanding margins",
                "Raised guidance after beating Q3 earnings expectations",
            ],
            bear_case=[
                "iPhone sales in China declined for a third consecutive quarter",
                "Trailing P/E of 35.2 is rich relative to the sector",
            ],
            notable_signals=["RSI at 58.3, price above the 50-day SMA"],
            data_quality_flags=[],
        ),
    )

    result = advisor_decide(state)
    decision = result["decision"]

    assert isinstance(decision, AdvisorDecision)
    assert decision.key_drivers
    assert decision.reasoning
