from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Message
from chat.models import ChatRoom  #  your model is


@login_required
def room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    # Check permission
    if request.user not in [room.user1, room.user2]:
        return JsonResponse({"error": "Not allowed"}, status=403)

    return render(request, "chat/room.html", {
        "room": room
    })


@login_required
def fetch_messages(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    messages = Message.objects.filter(room=room).values(
        "sender__username",
        "text",
        "timestamp"
    )

    return JsonResponse(list(messages), safe=False)


@login_required
def send_message(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    text = request.POST.get("text")

    if text.strip() == "":
        return JsonResponse({"error": "Empty message"}, status=400)

    Message.objects.create(
        room=room,
        sender=request.user,
        text=text
    )

    return JsonResponse({"status": "sent"})


def chat_list(request):
    rooms = ChatRoom.objects.filter(user1=request.user) | ChatRoom.objects.filter(user2=request.user)
    return render(request, 'chat/chat_list.html', {'rooms': rooms})