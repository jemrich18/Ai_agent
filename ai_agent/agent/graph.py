from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from agent.state import AgentState
from agent.tools import get_weather, calculate, search_hunting_knowledge

load_dotenv()

tools = [get_weather, calculate, search_hunting_knowledge]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools)

SYSTEM_PROMPT = """You are an expert hunting and archery assistant with deep knowledge of:
- OTC and draw tag availability by state and species
- Bow tuning, arrow building, and archery equipment
- Kinetic energy and momentum requirements for ethical hunting
- Whitetail rut phases and deer behavior
- Preference points and western draw systems
- Hunting regulations and license fees

Always use the search_hunting_knowledge tool first when answering hunting questions.
After using the tool, provide a clear, structured answer with specific details.
Always remind users to verify current prices and regulations with their state wildlife agency
before purchasing tags — regulations change annually.
Be direct and specific. Hunters want real answers, not vague generalities."""


def call_llm(state: AgentState) -> AgentState:
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
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