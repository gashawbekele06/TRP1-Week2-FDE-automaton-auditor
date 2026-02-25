import sys
from pathlib import Path

# Add the project root to sys.path to allow absolute imports when run directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from src.state import AgentState
from src.nodes.setup import setup_node
from src.nodes.repo_investigator import repo_investigator_node
from src.nodes.doc_analyst import doc_analyst_node
from src.nodes.aggregator import evidence_aggregator
from src.nodes.judges import judge_node
from src.nodes.justice import chief_justice_node


graph = StateGraph(AgentState)

# Nodes
graph.add_node("setup", setup_node)
graph.add_node("repo_investigator", repo_investigator_node)
graph.add_node("doc_analyst", doc_analyst_node)
graph.add_node("aggregator", evidence_aggregator)

graph.add_node("prosecutor", lambda s: judge_node(s, "Prosecutor"))
graph.add_node("defense", lambda s: judge_node(s, "Defense"))
graph.add_node("techlead", lambda s: judge_node(s, "TechLead"))

graph.add_node("justice", chief_justice_node)

graph.add_edge(START, "setup")

# Parallel detectives
def fan_out_detectives(state: AgentState):
    return [
        Send("repo_investigator", state),
        Send("doc_analyst", state),
        # Add Send("vision_investigator", state) later
    ]

graph.add_conditional_edges("setup", fan_out_detectives)

graph.add_edge(["repo_investigator", "doc_analyst"], "aggregator")

# Parallel judges per dimension
def fan_out_judges(state: AgentState):
    if state["current_dimension_index"] >= len(state["rubric_dimensions"]):
        return [Send("justice", state)]
    return [
        Send("prosecutor", state),
        Send("defense", state),
        Send("techlead", state),
    ]

graph.add_conditional_edges("aggregator", fan_out_judges)

# Loop back until all dimensions done
graph.add_edge(["prosecutor", "defense", "techlead"], "aggregator")

# Final justice
graph.add_edge("justice", END)

app = graph.compile()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--pdf", required=True)
    args = parser.parse_args()

    result = app.invoke({
        "repo_url": args.repo,
        "pdf_path": args.pdf,
    })
    print("Final Report:")
    print(result["final_report"])