from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from agent.state import AgentState
from agent.tools import get_weather, calculate, search_knowledge_base

load_dotenv()

tools = [get_weather, calculate, search_knowledge_base]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools)

SYSTEM_PROMPT = """You are a helpful assistant with access to the following tools:
- get_weather: get real-time weather for any city
- calculate: evaluate math expressions
- search_knowledge_base: search for information on Python, Django, and LangGraph

Always use a tool when the question calls for one. Be concise and direct in your responses.
If you cannot answer something with your available tools, say so clearly."""


def call_llm(state: AgentState) -> AgentState:
    """Node 1: send messages to the LLM, get a response back."""
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    """The router — checks if the LLM wants to call a tool or is done."""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "run_tools"
    return END


def build_graph(checkpointer=None):
    graph = StateGraph(AgentState)

    graph.add_node("llm", call_llm)
    graph.add_node("tools", ToolNode(tools))

    graph.set_entry_point("llm")

    graph.add_conditional_edges(
        "llm",
        should_continue,
        {
            "run_tools": "tools",
            END: END,
        }
    )

    graph.add_edge("tools", "llm")

    return graph.compile(checkpointer=checkpointer)