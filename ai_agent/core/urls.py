from django.contrib import admin
from django.urls import path, include
from api.views import chat_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', chat_view, name='chat-ui'),
]