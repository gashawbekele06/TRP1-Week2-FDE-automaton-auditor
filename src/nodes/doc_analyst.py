from typing import Dict, List
from src.state import AgentState, Evidence
from src.tools.doc_tools import ingest_pdf, query_pdf, extract_cited_filepaths

def doc_analyst_node(state: AgentState) -> Dict:
    """Executes target_artifact='pdf_report' forensics."""
    print("--- DOC ANALYST ---")
    pdf_path = state["pdf_path"]
    rubric = state["rubric_dimensions"]
    evidences: Dict[str, List[Evidence]] = {}

    chunks = ingest_pdf(pdf_path)
    
    for dimension in rubric:
        if dimension.get("target_artifact") != "pdf_report":
            continue
            
        dim_id = dimension["id"]
        evidences[dim_id] = []
        
        if dim_id == "theoretical_depth":
            keywords = ["Dialectical Synthesis", "Fan-In", "Fan-Out", "Metacognition", "State Synchronization"]
            keyword_evidence = query_pdf(chunks, keywords)
            
            for ev in keyword_evidence:
                 evidences[dim_id].append(Evidence(
                    goal=f"Determine presence of {ev['keyword']}",
                    found=True,
                    content=ev['context'][:500],
                    location="PDF Document context",
                    rationale="Keyword matched in docling chunk",
                    confidence=ev['confidence']
                ))
            if not keyword_evidence:
                 evidences[dim_id].append(Evidence(
                    goal="Determine theoretical depth",
                    found=False,
                    content="No relevant keywords found",
                    location="PDF report",
                    rationale="Docling iteration complete",
                    confidence=1.0
                ))

        elif dim_id == "report_accuracy":
             cited_paths = extract_cited_filepaths(chunks)
             
             if not cited_paths:
                   evidences[dim_id].append(Evidence(
                    goal="Extract file paths from PDF",
                    found=False,
                    content="No structured file paths cited in text.",
                    location="PDF Document context",
                    rationale="Naive extraction found no paths.",
                    confidence=0.8
                ))
             else:
                   evidences[dim_id].append(Evidence(
                        goal="Extract file paths from PDF",
                        found=True,
                        content=f"Report cites files: {', '.join(cited_paths)}",
                        location="PDF Document context",
                        rationale="Paths extracted.",
                        confidence=0.8
                    ))

    return {"evidences": evidences}
