from django.urls import path
from . import views

urlpatterns = [
    path("", views.chat_list, name="chat_list"),
    path("room/<int:room_id>/", views.room, name="room"),
    path("room/<int:room_id>/messages/", views.fetch_messages, name="fetch_messages"),
    path("room/<int:room_id>/send/", views.send_message, name="send_message"),

    path("agora/token/<int:room_id>/", views.agora_token, name="agora_token"),

    path("room/<int:room_id>/start-call/", views.start_call_notification, name="start_call_notification"),
    path("room/<int:room_id>/check-call/", views.check_incoming_call, name="check_incoming_call"),

    path("call/<int:call_id>/accept/", views.accept_call, name="accept_call"),
    path("call/<int:call_id>/decline/", views.decline_call, name="decline_call"),
    path("call/<int:call_id>/status/", views.call_status, name="call_status"),
    path("call/<int:call_id>/end/", views.end_call_notification, name="end_call_notification"),
]