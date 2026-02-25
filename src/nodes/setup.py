from typing import Dict
import json
from src.state import AgentState

def setup_node(state: AgentState) -> Dict:
    """Initializes the investigation by ensuring rubric dimensions are present."""
    print("--- SETUP NODE ---")
    if not state.get("rubric_dimensions"):
        try:
            with open("rubric.json", "r", encoding="utf-8") as f:
                rubric_data = json.load(f)
            return {"rubric_dimensions": rubric_data["dimensions"]}
        except Exception as e:
            print(f"Error loading rubric: {e}")
            return {"rubric_dimensions": []}
    return {}
