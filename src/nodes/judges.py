from typing import Dict, List, Any
import json
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

from src.state import AgentState, JudicialOpinion, Evidence

def format_evidence_for_prompt(dimension_name: str, instruction: str, evidences: List[Evidence]) -> str:
    """Formats evidence objects into a readable text block for LLM judges."""
    if not evidences:
        return f"CRITERION: {dimension_name}\nINSTRUCTION: {instruction}\nEVIDENCE: No evidence collected.\n"
    
    text = f"CRITERION: {dimension_name}\nINSTRUCTION: {instruction}\nEVIDENCE COLLECTED:\n"
    for ev in evidences:
         text += f"- Goal: {ev.goal}\n  Found: {ev.found}\n  Content: {ev.content}\n  Location: {ev.location}\n  Rationale: {ev.rationale}\n  Confidence: {ev.confidence}\n"
    return text


def create_judge_node(persona: str, system_prompt_basis: str):
    """Factory function for creating distinct Judicial Nodes."""
    def judge_node(state: AgentState) -> Dict:
        print(f"--- JUDGE: {persona} ---")
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
        structured_llm = llm.with_structured_output(JudicialOpinion)
        
        rubric = state["rubric_dimensions"]
        all_evidences = state.get("evidences", {})
        opinions: List[JudicialOpinion] = []
        
        for dimension in rubric:
            dim_id = dimension["id"]
            dim_name = dimension["name"]
            instruction = dimension.get("forensic_instruction", "")
            
            evidences_for_dim = all_evidences.get(dim_id, [])
            evidence_text = format_evidence_for_prompt(dim_name, instruction, evidences_for_dim)
            
            # Persona-Specific System Prompting
            prompt = f"""You are the {persona} in a Digital Courtroom.
            
            {system_prompt_basis}
            
            Your task is to review the following evidence collected by Detectives and render a JudicialOpinion regarding the developer's implementation of the `{dim_name}` criterion.
            
            Rule 1: Base your judgment ONLY on the provided evidence. If evidence is missing, state it.
            Rule 2: You MUST return a score between 1 and 5.
            Rule 3: Your `argument` must reflect your persona's specific philosophy and address the evidence directly.
            Rule 4: Cite specific 'Location' or 'Content' snippets in `cited_evidence`.
            
            {evidence_text}
            """
            
            try:
                opinion = structured_llm.invoke([SystemMessage(content=prompt), HumanMessage(content="Render your judgment.")])
                opinion.judge = persona
                opinion.criterion_id = dim_id
                opinions.append(opinion)
            except Exception as e:
                # Handle structured parse error via retry or fallback
                print(f"[{persona}] Error rendering opinion for {dim_id}: {e}")
                fallback = JudicialOpinion(
                     judge=persona,
                     criterion_id=dim_id,
                     score=3,
                     argument=f"Parsing error occurred during judgment: {str(e)}",
                     cited_evidence=[]
                )
                opinions.append(fallback)
                
        return {"opinions": opinions}
    return judge_node

prosecutor_prompt = """Core Philosophy: "Trust No One. Assume Vibe Coding."
Objective: Scrutinize the evidence for gaps, security flaws, and laziness. Look for 'Orchestration Fraud', linear pipelines masked as swarms, or missing validations. If Judges return freeform text instead of Pydantic models, charge the defendant with 'Hallucination Liability'. Be harsh and critical. Point out what is missing."""

defense_prompt = """Core Philosophy: "Reward Effort and Intent. Look for the 'Spirit of the Law'."
Objective: Highlight creative workarounds, deep thought, and effort, even if the implementation is imperfect. If code is buggy but the architecture report shows deep understanding, argue they match the 'Master Thinker' profile. Be generous. Look at Git History for struggle and iteration."""

techlead_prompt = """Core Philosophy: "Does it actually work? Is it maintainable?"
Objective: Evaluate architectural soundness, code cleanliness, and practical viability. Ignore the 'Vibe' and 'Struggle'. Focus on Artifacts. Are the state reducers (operator.add) actually used? Are tools sandboxed? Provide a realistic score and technical remediation advice. Act as the tie-breaker."""


prosecutor_node = create_judge_node("Prosecutor", prosecutor_prompt)
defense_node = create_judge_node("Defense", defense_prompt)
techlead_node = create_judge_node("TechLead", techlead_prompt)
