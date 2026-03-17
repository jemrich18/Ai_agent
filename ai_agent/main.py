from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from agent.graph import build_graph

load_dotenv()

# MemorySaver stores conversation history in memory between turns
memory = MemorySaver()
agent = build_graph(checkpointer=memory)

# thread_id ties messages together into one conversation session
config = {"configurable": {"thread_id": "session_1"}}

def run_agent(user_input: str):
    result = agent.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=config
    )
    return result["messages"][-1].content

print("Agent ready. Type 'quit' to exit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break
    response = run_agent(user_input)
    print(f"Agent: {response}\n")