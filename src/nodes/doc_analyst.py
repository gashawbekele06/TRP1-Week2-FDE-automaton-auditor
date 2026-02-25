from src.state import AgentState, Evidence
from src.tools.doc_tools import ingest_pdf, query_pdf_chunks


def doc_analyst_node(state: AgentState) -> AgentState:
    dim = state["rubric_dimensions"][state["current_dimension_index"]]
    evidence_list = []

    pdf_result = ingest_pdf.invoke({"pdf_path": state["pdf_path"]})
    chunks = pdf_result["chunks"]
    relevant = query_pdf_chunks.invoke({"chunks": chunks, "query": dim["name"]})
    evidence_list.append(Evidence(
        goal="PDF content scan",
        found=bool(relevant),
        content=relevant[0][:200] if relevant else "",
        location=state["pdf_path"],
        rationale="Chunk query complete",
        confidence=0.95
    ))

    dim_id = dim["id"]
    if dim_id not in state["evidences"]:
        state["evidences"][dim_id] = []
    state["evidences"][dim_id].extend(evidence_list)
    return state