from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from agent.graph import build_graph
from dotenv import load_dotenv

load_dotenv()

memory = MemorySaver()
agent = build_graph(checkpointer=memory)


class AgentView(APIView):
    def post(self, request):
        user_message = request.data.get("message")
        session_id = request.data.get("session_id", "default")

        if not user_message:
            return Response(
                {"error": "message field is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        config = {"configurable": {"thread_id": session_id}}

        result = agent.invoke(
            {"messages": [HumanMessage(content=user_message)]},
            config=config
        )

        response_text = result["messages"][-1].content

        return Response({
            "message": response_text,
            "session_id": session_id
        })


def chat_view(request):
    return render(request, "chat.html")