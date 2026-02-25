import os
from src.state import AgentState, CriterionResult, AuditReport, JudicialOpinion


def chief_justice_node(state: AgentState) -> AgentState:
    rubric = state["rubric"]
    rules = rubric.get("synthesis_rules", {})
    dimensions = rubric["dimensions"]

    criteria = []
    total = 0

    for dim in dimensions:
        dim_id = dim["id"]
        opinions = [op for op in state["opinions"] if op["criterion_id"] == dim_id]
        if len(opinions) != 3:
            continue

        pros, defe, tech = [op for op in opinions if op["judge"] == j for j in ["Prosecutor", "Defense", "TechLead"]]
        scores = [pros.score, defe.score, tech.score]
        variance = max(scores) - min(scores)

        final = round((tech.score * 0.5) + (sum(scores) / 3 * 0.5))

        dissent = None
        if variance > 2:
            dissent = f"Variance {variance}: Prosecutor ({pros.score}): {pros.argument[:100]}...; Defense ({defe.score}): {defe.argument[:100]}...; TechLead resolved."

        # Apply rules
        if "security" in pros.argument.lower() or "os.system" in pros.argument.lower():
            final = min(final, 3)
        if not defe.cited_evidence:
            final = pros.score
        if dim_id == "graph_orchestration" and tech.score >= 4:
            final = max(final, 4)

        remediation = tech.argument + " → " + dim["forensic_instruction"][:120] + "..."

        criteria.append(CriterionResult(
            dimension_id=dim_id,
            dimension_name=dim["name"],
            final_score=final,
            judge_opinions=opinions,
            dissent_summary=dissent,
            remediation=remediation
        ))
        total += final

    overall = total / len(criteria) if criteria else 0.0
    report = AuditReport(
        repo_url=state["repo_url"],
        executive_summary=f"Overall: {overall:.1f}/5. {len([c for c in criteria if c.final_score < 3])} critical issues.",
        overall_score=overall,
        criteria=criteria,
        remediation_plan="\n\n".join(c.remediation for c in criteria)
    )

    state["final_report"] = report

    path = "audit/report_onself_generated/audit_report.md"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("# Audit Report\n\n")
        f.write("## Executive Summary\n" + report.executive_summary + "\n\n")
        f.write("## Criterion Breakdown\n\n")
        for c in report.criteria:
            f.write(f"### {c.dimension_name} ({c.final_score}/5)\n")
            for op in c.judge_opinions:
                f.write(f"- **{op.judge}** ({op.score}): {op.argument}\n")
            if c.dissent_summary:
                f.write(f"**Dissent:** {c.dissent_summary}\n")
            f.write(f"**Remediation:** {c.remediation}\n\n")
        f.write("## Remediation Plan\n" + report.remediation_plan)

    return state