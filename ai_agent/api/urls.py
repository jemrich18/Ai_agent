from django.urls import path
from api.views import AgentView, chat_view

urlpatterns = [
    path('chat/', AgentView.as_view(), name='agent-chat'),
    path('', chat_view, name='chat-ui'),
]