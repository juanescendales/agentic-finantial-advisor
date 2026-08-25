import pytest
from langgraph.graph import END

from src.graph.schemas import CriticVerdict
from src.graph.state import AdvisorState
from src.nodes.critic import MAX_REVISIONS, route_after_critic


def _state(verdict: CriticVerdict | None, revision_count: int = 0) -> AdvisorState:
    return AdvisorState(
        ticker="AAPL", critic_verdict=verdict, revision_count=revision_count
    )


def _needs(branch: str) -> CriticVerdict:
    return CriticVerdict(
        status="needs_more",
        confidence_in_decision=0.4,
        needs_more=branch,
        feedback="earnings coverage for the latest quarter",
    )


@pytest.mark.parametrize(
    ("branch", "expected"),
    [
        ("news", "fetch_news"),
        ("fundamentals", "fetch_fundamentals"),
        ("market", "fetch_market"),
    ],
)
def test_routes_to_the_weak_branch(branch: str, expected: str) -> None:
    assert route_after_critic(_state(_needs(branch), revision_count=1)) == expected


def test_ends_when_verdict_is_ok() -> None:
    verdict = CriticVerdict(
        status="ok", confidence_in_decision=0.9, needs_more=None, feedback="solid"
    )
    assert route_after_critic(_state(verdict)) == END


def test_ends_when_no_verdict_was_produced() -> None:
    assert route_after_critic(_state(None)) == END


def test_allows_exactly_max_revisions_before_ending() -> None:
    """The last allowed revision is the one whose count equals MAX_REVISIONS."""
    for count in range(1, MAX_REVISIONS + 1):
        assert route_after_critic(_state(_needs("news"), count)) == "fetch_news"

    assert route_after_critic(_state(_needs("news"), MAX_REVISIONS + 1)) == END
