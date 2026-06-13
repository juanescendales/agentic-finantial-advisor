from src.graph.state import AdvisorState


def fetch_news(state: AdvisorState) -> dict[str, object]:
    raise NotImplementedError("fetch_news must populate news_data.")


def fetch_fundamentals(state: AdvisorState) -> dict[str, object]:
    raise NotImplementedError("fetch_fundamentals must populate fundamentals_data.")


def fetch_market(state: AdvisorState) -> dict[str, object]:
    raise NotImplementedError("fetch_market must populate market_data.")
