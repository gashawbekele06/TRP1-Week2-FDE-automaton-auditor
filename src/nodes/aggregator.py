from src.state import AgentState


def evidence_aggregator(state: AgentState) -> AgentState:
    # Validate all dimensions have evidence (reducer already merged)
    for dim in state["rubric_dimensions"]:
        dim_id = dim["id"]
        if dim_id not in state["evidences"]:
            state["evidences"][dim_id] = []
    return state