import pytest

from src.graph.schemas import NewsItem
from src.graph.state import AdvisorState
from src.nodes.fetchers import fetch_news


@pytest.mark.integration
def test_fetch_news_returns_populated_news_items() -> None:
    result = fetch_news(AdvisorState(ticker="AAPL", company_name="Apple Inc."))
    news_data = result["news_data"]

    assert isinstance(news_data, list)
    assert news_data
    assert all(isinstance(item, NewsItem) for item in news_data)
    assert all(item.title and item.url for item in news_data)
