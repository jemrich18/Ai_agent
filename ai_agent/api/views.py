import logging
import re

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from agent.graph import build_graph
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

memory = MemorySaver()
agent = build_graph(checkpointer=memory)

MAX_MESSAGE_LENGTH = 2000
_SESSION_ID_RE = re.compile(r'^[a-zA-Z0-9_\-]{1,64}$')


@method_decorator(csrf_exempt, name='dispatch')
class AgentView(APIView):
    def post(self, request):
        user_message = request.data.get("message")
        session_id = request.data.get("session_id", "default")

        if not user_message:
            return Response(
                {"error": "message field is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(user_message) > MAX_MESSAGE_LENGTH:
            return Response(
                {"error": f"Message exceeds {MAX_MESSAGE_LENGTH} character limit"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not _SESSION_ID_RE.match(str(session_id)):
            session_id = "default"

        config = {"configurable": {"thread_id": session_id}}

        try:
            result = agent.invoke(
                {"messages": [HumanMessage(content=user_message)]},
                config=config
            )
            response_text = result["messages"][-1].content
        except Exception:
            logger.exception("Agent invocation failed for session %s", session_id)
            return Response(
                {"error": "An error occurred processing your request. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            "message": response_text,
            "session_id": session_id
        })


def chat_view(request):
    return render(request, "chat.html")