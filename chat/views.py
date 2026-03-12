from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
import time

from agora_token_builder import RtcTokenBuilder

from .models import Message, ChatRoom, Call


def user_has_room_access(user, room):
    return user == room.user1 or user == room.user2


@login_required
def room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    if not user_has_room_access(request.user, room):
        return JsonResponse({"error": "Not allowed"}, status=403)

    other_user = room.user2 if request.user == room.user1 else room.user1

    return render(request, "chat/room.html", {
        "room": room,
        "other_user": other_user,
    })


@login_required
def fetch_messages(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    if not user_has_room_access(request.user, room):
        return JsonResponse({"error": "Not allowed"}, status=403)

    messages = Message.objects.filter(room=room).order_by("timestamp")

    data = []
    for m in messages:
        data.append({
            "id": m.id,
            "sender": m.sender.username,
            "text": m.text or "",
            "image": m.image.url if m.image else None,
            "timestamp": m.timestamp.isoformat() if m.timestamp else None,
        })

    return JsonResponse(data, safe=False)


@login_required
def send_message(request, room_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    room = get_object_or_404(ChatRoom, id=room_id)

    if not user_has_room_access(request.user, room):
        return JsonResponse({"error": "Not allowed"}, status=403)

    text = request.POST.get("text", "").strip()
    image = request.FILES.get("image")

    if not text and not image:
        return JsonResponse({"error": "Empty message"}, status=400)

    message = Message.objects.create(
        room=room,
        sender=request.user,
        text=text,
        image=image
    )

    return JsonResponse({
        "status": "sent",
        "message": {
            "id": message.id,
            "sender": message.sender.username,
            "text": message.text or "",
            "image": message.image.url if message.image else None,
            "timestamp": message.timestamp.isoformat() if message.timestamp else None,
        }
    })


@login_required
def chat_list(request):
    rooms = (
        ChatRoom.objects.filter(user1=request.user) |
        ChatRoom.objects.filter(user2=request.user)
    ).distinct()

    rooms_with_other = []

    for room in rooms:
        other_user = room.user2 if room.user1 == request.user else room.user1
        last_message = Message.objects.filter(room=room).order_by("-timestamp").first()

        rooms_with_other.append({
            "room": room,
            "other_user": other_user,
            "last_message": last_message,
        })

    return render(request, "chat/chat_list.html", {
        "rooms": rooms_with_other
    })


def start_or_get_chat_room(user1, user2):
    user_ids = sorted([user1.id, user2.id])

    first_user = User.objects.get(id=user_ids[0])
    second_user = User.objects.get(id=user_ids[1])

    room, created = ChatRoom.objects.get_or_create(
        user1=first_user,
        user2=second_user
    )

    return room


@login_required
def agora_token(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    if not user_has_room_access(request.user, room):
        return JsonResponse({"error": "Not allowed"}, status=403)

    app_id = getattr(settings, "AGORA_APP_ID", None)
    app_certificate = getattr(settings, "AGORA_APP_CERTIFICATE", None)

    if not app_id:
        return JsonResponse({"error": "AGORA_APP_ID is missing in settings.py"}, status=500)

    if not app_certificate:
        return JsonResponse({"error": "AGORA_APP_CERTIFICATE is missing in settings.py"}, status=500)

    try:
        channel_name = f"room_{room_id}"
        uid = str(request.user.id)
        role = 1
        expire_time_in_seconds = 3600
        current_timestamp = int(time.time())
        privilege_expired_ts = current_timestamp + expire_time_in_seconds

        token = RtcTokenBuilder.buildTokenWithAccount(
            app_id,
            app_certificate,
            channel_name,
            uid,
            role,
            privilege_expired_ts
        )

        return JsonResponse({
            "token": token,
            "appId": app_id,
            "channel": channel_name,
            "uid": uid
        })

    except Exception as e:
        return JsonResponse({
            "error": "Failed to generate Agora token",
            "details": str(e)
        }, status=500)


@login_required
def start_call_notification(request, room_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    room = get_object_or_404(ChatRoom, id=room_id)

    if not user_has_room_access(request.user, room):
        return JsonResponse({"error": "Not allowed"}, status=403)

    call_type = request.POST.get("call_type", "voice")
    if call_type not in ["voice", "video"]:
        return JsonResponse({"error": "Invalid call type"}, status=400)

    receiver = room.user2 if request.user == room.user1 else room.user1

    # avoid duplicate active call rows
    old_calls = Call.objects.filter(
        room=room,
        caller=request.user,
        receiver=receiver,
        status="calling"
    )
    if old_calls.exists():
        old_calls.update(status="missed")

    call = Call.objects.create(
        room=room,
        caller=request.user,
        receiver=receiver,
        call_type=call_type,
        status="calling"
    )

    return JsonResponse({
        "status": "ok",
        "call_id": call.id
    })


@login_required
def check_incoming_call(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)

    if not user_has_room_access(request.user, room):
        return JsonResponse({"error": "Not allowed"}, status=403)

    call = Call.objects.filter(
        room=room,
        receiver=request.user,
        status="calling"
    ).order_by("-created_at").first()

    if not call:
        return JsonResponse({"incoming": False})

    return JsonResponse({
        "incoming": True,
        "call_id": call.id,
        "caller": call.caller.username,
        "call_type": call.call_type
    })


@login_required
def accept_call(request, call_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    call = get_object_or_404(Call, id=call_id)

    if call.receiver != request.user:
        return JsonResponse({"error": "Not allowed"}, status=403)

    call.status = "accepted"
    call.save()

    return JsonResponse({
        "status": "accepted",
        "call_type": call.call_type
    })


@login_required
def decline_call(request, call_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    call = get_object_or_404(Call, id=call_id)

    if call.receiver != request.user:
        return JsonResponse({"error": "Not allowed"}, status=403)

    call.status = "declined"
    call.save()

    return JsonResponse({"status": "declined"})


@login_required
def call_status(request, call_id):
    call = get_object_or_404(Call, id=call_id)

    if request.user != call.caller and request.user != call.receiver:
        return JsonResponse({"error": "Not allowed"}, status=403)

    return JsonResponse({
        "status": call.status,
        "call_type": call.call_type
    })


@login_required
def end_call_notification(request, call_id):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    call = get_object_or_404(Call, id=call_id)

    if request.user != call.caller and request.user != call.receiver:
        return JsonResponse({"error": "Not allowed"}, status=403)

    call.status = "ended"
    call.save()

    return JsonResponse({"status": "ended"})