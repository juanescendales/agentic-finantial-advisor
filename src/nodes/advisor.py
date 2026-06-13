from src.graph.state import AdvisorState


def advisor_decide(state: AdvisorState) -> dict[str, object]:
    raise NotImplementedError("advisor_decide must populate decision.")
