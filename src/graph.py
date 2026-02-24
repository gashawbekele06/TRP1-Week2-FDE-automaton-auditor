import json
import os
from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send

from src.state import AgentState, AuditReport
from src.nodes.detectives import repo_investigator, doc_analyst, vision_inspector
from src.nodes.judges import prosecutor_node, defense_node, techlead_node
from src.nodes.justice import chief_justice_node

def evidence_aggregator(state: AgentState):
    """Synchronization node (Fan-In) before judges."""
    print("--- EVIDENCE AGGREGATED ---")
    return {"evidences": state.get("evidences", {})}


def format_report_to_markdown(report: AuditReport, output_path: str):
    """Serializes AuditReport model into a structured Markdown file."""
    md_content = f"# Automaton Auditor: Final Report\n\n"
    md_content += f"**Target Repository:** {report.repo_url}\n\n"
    
    md_content += f"## Executive Summary\n"
    md_content += f"> {report.executive_summary}\n\n"
    md_content += f"**Overall Audit Score:** {report.overall_score:.2f} / 5.0\n\n"
    
    md_content += f"## Criterion Breakdown\n\n"
    for criterion in report.criteria:
        md_content += f"### {criterion.dimension_name} (Score: {criterion.final_score}/5)\n\n"
        
        md_content += "#### The Dialectical Bench Opinions\n"
        for opinion in criterion.judge_opinions:
            md_content += f"* **The {opinion.judge}**: {opinion.argument} (Score: {opinion.score})\n"
            if opinion.cited_evidence:
                 # Optional: add rendered citations if not too verbose
                 pass
                 
        if criterion.dissent_summary:
            md_content += f"\n> **Chief Justice Dissent Summary:** {criterion.dissent_summary}\n\n"
            
        md_content += f"**Remediation:** {criterion.remediation}\n\n"
        md_content += "---\n\n"
        
    md_content += f"## Remediation Plan\n"
    md_content += f"{report.remediation_plan}\n"
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
         f.write(md_content)
         
    print(f"\n[+] Report exported to: {output_path}")


def build_auditor_graph() -> StateGraph:
    """Constructs the Deep LangGraph Swarm architecture."""
    workflow = StateGraph(AgentState)
    
    # Layer 1: The Detective Layer
    workflow.add_node("RepoInvestigator", repo_investigator)
    workflow.add_node("DocAnalyst", doc_analyst)
    workflow.add_node("VisionInspector", vision_inspector)
    
    # Layer 2: Aggregation
    workflow.add_node("EvidenceAggregator", evidence_aggregator)
    
    # Layer 3: The Judicial Layer
    # Note: These use the same underlying state so they can act on 'evidences' concurrently
    workflow.add_node("Prosecutor", prosecutor_node)
    workflow.add_node("Defense", defense_node)
    workflow.add_node("TechLead", techlead_node)
    
    # Layer 4: The Supreme Court
    workflow.add_node("ChiefJustice", chief_justice_node)
    
    # Mapping
    # Fan-Out 1 to Detectives
    workflow.add_edge(START, "RepoInvestigator")
    workflow.add_edge(START, "DocAnalyst")
    workflow.add_edge(START, "VisionInspector")
    
    # Fan-In 1 to Evidence Aggregator
    workflow.add_edge("RepoInvestigator", "EvidenceAggregator")
    workflow.add_edge("DocAnalyst", "EvidenceAggregator")
    workflow.add_edge("VisionInspector", "EvidenceAggregator")
    
    # Fan-Out 2 to Judges
    workflow.add_edge("EvidenceAggregator", "Prosecutor")
    workflow.add_edge("EvidenceAggregator", "Defense")
    workflow.add_edge("EvidenceAggregator", "TechLead")
    
    # Fan-In 2 to Chief Justice
    workflow.add_edge("Prosecutor", "ChiefJustice")
    workflow.add_edge("Defense", "ChiefJustice")
    workflow.add_edge("TechLead", "ChiefJustice")
    
    workflow.add_edge("ChiefJustice", END)
    
    return workflow.compile()


if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv
    
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Run the Automaton Auditor Swarm.")
    parser.add_argument("--repo", type=str, required=True, help="GitHub repository URL to evaluate")
    parser.add_argument("--pdf", type=str, required=True, help="Path to the PDF architectural report")
    parser.add_argument("--output", type=str, default="audit/report_onself_generated.md", help="Path to save the final Markdown report.")
    args = parser.parse_args()
    
    with open("rubric.json", "r", encoding="utf-8") as f:
         rubric_data = json.load(f)
         
    initial_state = {
        "repo_url": args.repo,
        "pdf_path": args.pdf,
        "rubric_dimensions": rubric_data["dimensions"],
        "synthesis_rules": rubric_data["synthesis_rules"],
        "evidences": {},
        "opinions": []
    }
    
    print(f"Starting Automaton Auditor for {args.repo}...")
    app = build_auditor_graph()
    
    final_output = app.invoke(initial_state)
    report = final_output.get("final_report")
    if report:
         format_report_to_markdown(report, args.output)
    else:
         print("Execution failed to produce a final report.")
