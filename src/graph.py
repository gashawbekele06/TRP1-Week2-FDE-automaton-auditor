import json
import argparse
import sys
import os

# Ensure the project root is on the path so `src` is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from src.state import AgentState
from src.nodes.setup import setup_node
from src.nodes.repo_investigator import repo_investigator_node
from src.nodes.doc_analyst import doc_analyst_node
from src.nodes.aggregator import evidence_aggregator

def fan_out_detectives(state: AgentState):
    """Fan-out to detective nodes."""
    return [
        Send("repo_investigator", state),
        Send("doc_analyst", state),
    ]

def build_graph() -> StateGraph:
    """Constructs the research graph."""
    workflow = StateGraph(AgentState)

    workflow.add_node("setup", setup_node)
    workflow.add_node("repo_investigator", repo_investigator_node)
    workflow.add_node("doc_analyst", doc_analyst_node)
    workflow.add_node("aggregator", evidence_aggregator)

    workflow.add_edge(START, "setup")
    workflow.add_conditional_edges("setup", fan_out_detectives)
    
    # In LangGraph, fan-in from multiple Send calls is handled by the common aggregator node
    # Since we used Send(), we don't need a direct list edge from individual nodes to aggregator
    # if those nodes weren't added as standard nodes. 
    # BUT here they ARE standard nodes in add_node.
    # If they are standard nodes, we use normal edges.
    
    workflow.add_edge("repo_investigator", "aggregator")
    workflow.add_edge("doc_analyst", "aggregator")
    workflow.add_edge("aggregator", END)

    return workflow.compile()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    parser = argparse.ArgumentParser(description="Run the Automaton Auditor Swarm.")
    parser.add_argument("--repo", type=str, required=True, help="GitHub repository URL")
    parser.add_argument("--pdf", type=str, required=True, help="Path to the PDF report")
    args = parser.parse_args()

    # Load initial data if needed (setup_node handles it too, but we can pass it)
    with open("rubric.json", "r", encoding="utf-8") as f:
         rubric_data = json.load(f)

    initial_state = {
        "repo_url": args.repo,
        "pdf_path": args.pdf,
        "rubric_dimensions": rubric_data["dimensions"],
        "evidences": {},
        "opinions": []
    }

    print(f"Starting Automaton Auditor for {args.repo}...")
    app = build_graph()

    final_output = app.invoke(initial_state)
    print("\n--- EXECUTION COMPLETE ---")
