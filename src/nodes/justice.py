from typing import Dict, List, Any
import json
import statistics

from src.state import AgentState, JudicialOpinion, CriterionResult, AuditReport

def resolve_score_and_dissent(opinions: List[JudicialOpinion], rules: Dict[str, str], dimension_id: str) -> (int, str, str):
    """Applies hardcoded Python logic to determine final score and resolve dissent."""
    
    # Extract roles
    prosecutor_op = next((op for op in opinions if op.judge == "Prosecutor"), None)
    defense_op = next((op for op in opinions if op.judge == "Defense"), None)
    techlead_op = next((op for op in opinions if op.judge == "TechLead"), None)
    
    scores = [op.score for op in opinions if op]
    if not scores:
         return 3, "No opinions submitted.", "Review execution logs."
         
    variance = max(scores) - min(scores)
    final_score = round(statistics.mean(scores))
    dissent_summary = ""
    remediation = ""
    
    # 1. Rule of Security Override
    if techlead_op and prosecutor_op and prosecutor_op.score <= 2 and "os.system" in prosecutor_op.argument.lower():
         if final_score > 3:
             final_score = 3
             dissent_summary += "SECURITY OVERRIDE APPLIED: Final score capped at 3 due to unsanitized os.system calls detected by Prosecutor. "
             
    # 2. Rule of Functionality Weight for Architecture
    if dimension_id == "graph_orchestration" and techlead_op:
         if techlead_op.score >= 4:
             final_score = max(final_score, 4)
             dissent_summary += "FUNCTIONALITY WEIGHT APPLIED: Tech Lead confirmed modular workable structure, outweighing negative variance. "
             
    # 3. Rule of Fact Supremacy (Hallucination Override)
    if "hallucination" in prosecutor_op.argument.lower() or "hallucination" in (techlead_op.argument.lower() if techlead_op else ""):
         if defense_op and defense_op.score >= 4:
              final_score = min(final_score, 3)
              dissent_summary += "FACT SUPREMACY APPLIED: Defense argument for effort overruled due to factually missing components. "
              
    if variance > 2:
         dissent_summary += f"HIGH VARIANCE DETECTED ({variance} pts): The Prosecutor argued '{prosecutor_op.argument[:100]}...' while Defense argued '{defense_op.argument[:100]}...'. Priority given to Tech Lead pragmatism. "
         
    # Generate generic remediation based on average
    if final_score <= 2:
         remediation = f"CRITICAL GAPS: Address {prosecutor_op.argument[:150]} immediately to stabilize this criterion."
    elif final_score == 3 or final_score == 4:
         remediation = f"MODERATE IMPROVEMENTS needed. Tech Lead notes: {techlead_op.argument[:150]}"
    else:
         remediation = "Excellent work. Continue iterative scaling of this pattern."
         
    return final_score, dissent_summary, remediation


def chief_justice_node(state: AgentState) -> Dict:
    """Consolidates evidence and opinions into final AuditReport Markdown."""
    print("--- CHIEF JUSTICE ---")
    
    repo_url = state["repo_url"]
    rubric = state["rubric_dimensions"]
    synthesis_rules = state.get("synthesis_rules", {})
    opinions = state.get("opinions", [])
    
    criterion_results: List[CriterionResult] = []
    overall_sum = 0
    
    for dimension in rubric:
         dim_id = dimension["id"]
         dim_name = dimension["name"]
         
         # Filter opinions for this dimension
         dim_opinions = [op for op in opinions if op.criterion_id == dim_id]
         
         if not dim_opinions:
              continue
              
         score, dissent, remediation = resolve_score_and_dissent(dim_opinions, synthesis_rules, dim_id)
         overall_sum += score
         
         result = CriterionResult(
             dimension_id=dim_id,
             dimension_name=dim_name,
             final_score=score,
             judge_opinions=dim_opinions,
             dissent_summary=dissent if dissent else None,
             remediation=remediation
         )
         criterion_results.append(result)
         
    num_criteria = len(criterion_results)
    overall_score = overall_sum / num_criteria if num_criteria > 0 else 0.0
    
    executive_summary = "Audit complete. "
    if overall_score >= 4.0:
        executive_summary += "System resembles a robust 'Master Thinker' Swarm architecture."
    elif overall_score >= 3.0:
        executive_summary += "System displays 'Competent Orchestration', but maintains technical debt."
    else:
        executive_summary += "System leans toward a 'Vibe Coder' implementation; critical structural improvements required."
        
    final_report = AuditReport(
        repo_url=repo_url,
        executive_summary=executive_summary,
        overall_score=overall_score,
        criteria=criterion_results,
        remediation_plan="Refer to criterion-level remediation steps below."
    )
    
    return {"final_report": final_report}
