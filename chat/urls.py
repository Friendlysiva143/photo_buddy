from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_list, name='chat_list'),  # <-- this is the key
    path("room/<int:room_id>/", views.room, name="chat_room"),
    path("room/<int:room_id>/messages/", views.fetch_messages, name="fetch_messages"),
    path("room/<int:room_id>/send/", views.send_message, name="send_message"),
]
