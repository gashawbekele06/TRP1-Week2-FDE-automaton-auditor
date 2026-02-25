from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from src.state import AgentState, JudicialOpinion


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)


def create_judge_chain(judge_type: str) -> any:
    if judge_type == "Prosecutor":
        system = "You are the Prosecutor. Be harsh, assume vibe coding. Scrutinize gaps, security, laziness."
    elif judge_type == "Defense":
        system = "You are the Defense. Reward effort, intent, creative workarounds. Look for spirit of the law."
    else:
        system = "You are the Tech Lead. Pragmatic. Focus on maintainability, soundness, viability."

    prompt = ChatPromptTemplate.from_messages([
        ("system", system + "\n{rubric_logic} Return JudicialOpinion JSON."),
        ("human", "Evidence: {evidence}\nDimension: {dim_name}"),
    ])

    chain = prompt | llm.with_structured_output(JudicialOpinion)
    return chain


def judge_node(state: AgentState, judge_type: str) -> AgentState:
    idx = state["current_dimension_index"] - 1
    dim = state["rubric_dimensions"][idx]
    evidence = state["evidences"].get(dim["id"], [])

    chain = create_judge_chain(judge_type)

    opinion = chain.invoke({
        "rubric_logic": dim["judicial_logic"][judge_type.lower()],
        "dim_name": dim["name"],
        "evidence": str(evidence),
    })

    opinion["judge"] = judge_type
    opinion["criterion_id"] = dim["id"]

    state["opinions"].append(opinion)
    return state