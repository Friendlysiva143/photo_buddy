from django.urls import path
from .views import demo_chat_list, demo_chat_conversation

urlpatterns = [
    path('demo_chats/', demo_chat_list, name='demo_chat_list'),
    path('demo_chat/<int:buddy_id>/', demo_chat_conversation, name='demo_chat_conversation'),
]
