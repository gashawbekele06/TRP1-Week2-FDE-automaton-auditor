from src.state import AgentState, Evidence
from src.tools.repo_tools import analyze_graph_structure, extract_git_history


def repo_investigator_node(state: AgentState) -> AgentState:
    dim = state["rubric_dimensions"][state["current_dimension_index"]]
    evidence_list = []

    graph_analysis = analyze_graph_structure.invoke({"repo_path": state["repo_path"]})
    git_hist = extract_git_history.invoke({"repo_path": state["repo_path"]})
    evidence_list.append(Evidence(
        goal="Graph structure & git history",
        found=graph_analysis["stategraph_found"],
        location=state["repo_path"],
        rationale=str(graph_analysis) + str(git_hist),
        confidence=0.9
    ))

    dim_id = dim["id"]
    if dim_id not in state["evidences"]:
        state["evidences"][dim_id] = []
    state["evidences"][dim_id].extend(evidence_list)
    return state