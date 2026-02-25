import json
import os
from src.state import AgentState
from src.tools.repo_tools import safe_git_clone
from src.tools.doc_tools import ingest_pdf


def setup_node(state: AgentState) -> AgentState:
    clone_result = safe_git_clone.invoke({"repo_url": state["repo_url"]})
    if not clone_result["success"]:
        raise RuntimeError("Clone failed")

    state["repo_path"] = clone_result["path"]

    pdf_result = ingest_pdf.invoke({"pdf_path": state["pdf_path"]})
    state["pdf_chunks"] = pdf_result["chunks"]

    rubric_path = os.path.join(os.path.dirname(__file__), "../../rubric/week2_rubric.json")
    with open(rubric_path, "r") as f:
        state["rubric"] = json.load(f)
    state["rubric_dimensions"] = state["rubric"]["dimensions"]

    state["current_dimension_index"] = 0
    state["evidences"] = {}
    state["opinions"] = []

    return state