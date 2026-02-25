from typing import Dict
from src.state import AgentState

def evidence_aggregator(state: AgentState) -> Dict:
    """Synchronization node (Fan-In) collecting all evidence."""
    print("\n--- EVIDENCE AGGREGATED ---")
    evidences = state.get("evidences", {})
    for dim, ev_list in evidences.items():
        print(f"Dimension: {dim} - Found {len(ev_list)} evidence items.")
        for ev in ev_list:
             print(f"  - [{ev.found}] {ev.goal}: {ev.rationale}")
    return {"evidences": evidences}
