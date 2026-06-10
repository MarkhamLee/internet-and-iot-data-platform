from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
import os

OLLAMA_URL = os.environ['OLLAMA_BASE_URL']
QWEN_MODEL = "qwen3.5:9b"

print(f'Up and running with Ollama instance at {OLLAMA_URL}')


@tool
def add_numbers(a: int, b: int) -> int:
    """Add two integers together."""
    return a + b


tools = [add_numbers]
llm = ChatOllama(model=QWEN_MODEL, base_url=OLLAMA_URL)
llm_with_tools = llm.bind_tools(tools)


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def call_model(state: AgentState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


def should_continue(state: AgentState):
    last = state["messages"][-1]
    return "tools" if last.tool_calls else END


graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("tools", ToolNode(tools))
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")
app_graph = graph.compile()
