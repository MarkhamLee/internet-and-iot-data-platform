from datetime import datetime, timezone, timedelta
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import os

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama.ollama.svc:11434")
llm = ChatOllama(model="qwen3:30b-a3b", base_url=OLLAMA_URL)

def route_alert(state: AlertAgentState) -> str:
    """Deterministic router — LLM never decides whether to research."""
    if state["skip_research"]:
        return "remind"
    if state["last_researched_at"] is None:
        return "research"
    age = datetime.now(timezone.utc) - state["last_researched_at"]
    return "remind" if age < timedelta(hours=24) else "research"

def research_node(state: AlertAgentState) -> dict:
    structured_llm = llm.with_structured_output(DependabotRiskAssessment)
    system = """You are a security-focused dependency analyst. Given:
    1. A GitHub Dependabot alert with CVE details
    2. The code in the repository that uses the vulnerable package  
    3. Registry data about the suggested upgrade version

    Assess the risk of applying the suggested upgrade. Focus specifically on whether
    the API surface used in the repository code has changed between the current and
    suggested versions. Be conservative: if changelog data is absent, rate breaking
    risk as 'medium' rather than 'low'."""
    
    user_prompt = f"""
    Alert: {state['alert_data']}
    Code context: {state['code_context']}
    Registry research: {state['registry_data']}
    """
    assessment = structured_llm.invoke([
        {"role": "system", "content": system},
        {"role": "user", "content": user_prompt}
    ])
    return {"assessment": assessment}

# Graph wiring
graph = StateGraph(AlertAgentState)
graph.add_node("fetch_alert", fetch_alert_node)       # calls GitHub API
graph.add_node("load_db_state", load_db_state_node)   # reads Postgres for last_researched_at
graph.add_node("fetch_code", fetch_code_node)         # GitHub Contents API
graph.add_node("research_registry", research_registry_node)  # PyPI/npm
graph.add_node("research", research_node)             # LLM assessment
graph.add_node("persist_research", persist_research_node)     # writes to Postgres
graph.add_node("send_report", send_report_node)       # Slack initial or updated message
graph.add_node("remind", remind_node)                 # Slack thread reminder

graph.set_entry_point("fetch_alert")
graph.add_edge("fetch_alert", "load_db_state")
graph.add_conditional_edges("load_db_state", route_alert, {
    "research": "fetch_code",
    "remind": "remind"
})
graph.add_edge("fetch_code", "research_registry")
graph.add_edge("research_registry", "research")
graph.add_edge("research", "persist_research")
graph.add_edge("persist_research", "send_report")
graph.add_edge("send_report", END)
graph.add_edge("remind", END)