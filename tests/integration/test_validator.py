import pytest

from src.graph.state import AdvisorState
from src.nodes.validator import validate_ticker


@pytest.mark.integration
def test_validate_ticker_sets_company_name_for_valid_ticker() -> None:
    result = validate_ticker(AdvisorState(ticker="AAPL"))
    company_name = result["company_name"]

    assert isinstance(company_name, str)
    assert "Apple" in company_name


@pytest.mark.integration
def test_validate_ticker_sets_errors_for_invalid_ticker() -> None:
    result = validate_ticker(AdvisorState(ticker="NOEXISTE123"))

    assert result["errors"]
