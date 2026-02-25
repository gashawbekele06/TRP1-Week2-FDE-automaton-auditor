import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Dict, List

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

from src.state import AgentState, Evidence
from src.tools.repo_tools import clone_repo_sandboxed, extract_git_history, analyze_graph_structure, check_file_exists
from src.tools.doc_tools import ingest_pdf, query_pdf, extract_cited_filepaths

def repo_investigator(state: AgentState) -> Dict:
    """Executes target_artifact='github_repo' forensics."""
    print("--- REPO INVESTIGATOR ---")
    repo_url = state["repo_url"]
    rubric = state["rubric_dimensions"]
    evidences: Dict[str, List[Evidence]] = {}

    try:
        temp_dir = clone_repo_sandboxed(repo_url)
        git_history = extract_git_history(temp_dir.name)
        ast_analysis = analyze_graph_structure(temp_dir.name)
        
        for dimension in rubric:
            if dimension.get("target_artifact") != "github_repo":
                continue
                
            dim_id = dimension["id"]
            evidences[dim_id] = []
            
            if dim_id == "git_forensic_analysis":
                evidences[dim_id].append(Evidence(
                    goal="Extract Git History Progression",
                    found=len(git_history.splitlines()) > 3,
                    content=git_history[:1000],  # Cap size
                    location="git log",
                    rationale="History extracted successfully",
                    confidence=1.0
                ))
            
            elif dim_id == "state_management_rigor":
                has_state = check_file_exists(temp_dir.name, "src/state.py") or check_file_exists(temp_dir.name, "src/graph.py")
                evidences[dim_id].append(Evidence(
                    goal="Verify State File Existence",
                    found=has_state,
                    content="src/state.py or src/graph.py detected",
                    location="src/state.py",
                    rationale="Verified file path",
                    confidence=1.0
                ))
                evidences[dim_id].append(Evidence(
                    goal="Verify Pydantic/TypedDict usage",
                    found=ast_analysis.has_pydantic or ast_analysis.has_typed_dict,
                    content=f"Pydantic: {ast_analysis.has_pydantic}, TypedDict: {ast_analysis.has_typed_dict}",
                    location="State classes",
                    rationale="Parsed AST for base classes",
                    confidence=0.9
                ))
                evidences[dim_id].append(Evidence(
                    goal="Verify Reducers",
                    found=len(ast_analysis.state_reducers) > 0,
                    content=f"Reducers found: {', '.join(ast_analysis.state_reducers)}",
                    location="Annotated type hints",
                    rationale="Parsed AST for operator usage in AnnAssign",
                    confidence=0.9
                ))

            elif dim_id == "graph_orchestration":
                 evidences[dim_id].append(Evidence(
                    goal="Verify StateGraph Definition",
                    found=ast_analysis.state_graph_instantiated,
                    content=f"Graph instantiated",
                    location="src/graph.py",
                    rationale="Parsed AST for StateGraph call",
                    confidence=0.9
                ))
                 evidences[dim_id].append(Evidence(
                    goal="Verify Fan-Out / Fan-In patterns",
                    found=len(ast_analysis.fan_out_fan_in_patterns) > 0,
                    content=f"Patterns matching edge logic: {', '.join(ast_analysis.fan_out_fan_in_patterns)}",
                    location="StateGraph routing",
                    rationale="Parsed AST for add_edge / conditional arguments",
                    confidence=0.8
                ))
                
            elif dim_id == "safe_tool_engineering":
                 evidences[dim_id].append(Evidence(
                    goal="Verify Git Sandboxing",
                    found=ast_analysis.use_tempfile,
                    content="tempfile.TemporaryDirectory usage detected.",
                    location="src/tools/",
                    rationale="Parsed tool files for tempfile instantiation.",
                    confidence=0.9
                ))
                 evidences[dim_id].append(Evidence(
                    goal="Security Violations",
                    found=ast_analysis.has_os_system,
                    content="os.system call detected - Potential Sandbox Break",
                    location="AST traversal",
                    rationale="Parsed os.system call",
                    confidence=0.9
                ))
                
            elif dim_id == "structured_output_enforcement":
                 evidences[dim_id].append(Evidence(
                    goal="Structured Output Usage",
                    found=ast_analysis.uses_structured_output,
                    content="with_structured_output or bind_tools parsed",
                    location="src/nodes/judges.py",
                    rationale="AST parsed judge definition",
                    confidence=0.9
                ))
                
        temp_dir.cleanup()
    except Exception as e:
        # Fallback evidence on crash
        evidences["git_forensic_analysis"] = [Evidence(
            goal="Clone and Extract Repo", found=False, content=str(e), location=repo_url, rationale="Clone Failed", confidence=0.0
        )]

    return {"evidences": evidences}


def doc_analyst(state: AgentState) -> Dict:
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

def vision_inspector(state: AgentState) -> Dict:
    """Placeholder for MultiModal vision extraction and description."""
    print("--- VISION INSPECTOR ---")
    evidences: Dict[str, List[Evidence]] = {}
    
    # Example logic matching rubric
    evidences["swarm_visual"] = [Evidence(
         goal="Architectural Diagram Analysis",
         found=False,
         content="Vision Inspector unimplemented in Phase 1 execution due to PDF image extraction complexity. Assuming simple linear flowchart for defensive logic.",
         location="PDF Diagram",
         rationale="Module Not Fully Executed",
         confidence=0.1
    )]
        
    return {"evidences": evidences}
