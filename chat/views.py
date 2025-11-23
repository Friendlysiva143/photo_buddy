from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Message
from chat.models import ChatRoom

@login_required
def room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    # Check permission: Only allow user1 or user2
    if request.user not in [room.user1, room.user2]:
        return JsonResponse({"error": "Not allowed"}, status=403)
    return render(request, "chat/room.html", {"room": room})

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
    text = request.POST.get("text", "")
    if text.strip() == "":
        return JsonResponse({"error": "Empty message"}, status=400)
    Message.objects.create(
        room=room,
        sender=request.user,
        text=text
    )
    return JsonResponse({"status": "sent"})

@login_required
def chat_list(request):
    rooms = (ChatRoom.objects.filter(user1=request.user) | ChatRoom.objects.filter(user2=request.user)).distinct()
    rooms_with_other = []
    for room in rooms:
        other_user = room.user2 if room.user1 == request.user else room.user1
        rooms_with_other.append({'room': room, 'other_user': other_user})
    return render(request, 'chat/chat_list.html', {'rooms': rooms_with_other})

# ---- ROOM CREATION LOGIC ----
# Call this whenever you want to create/start a chat between two users
def start_or_get_chat_room(user1, user2):
    # Always store rooms for each user pair by sorted user ids, so only one room per pair
    user_ids = sorted([user1.id, user2.id])
    room, created = ChatRoom.objects.get_or_create(
        user1=User.objects.get(id=user_ids[0]),
        user2=User.objects.get(id=user_ids[1])
    )
    return room
