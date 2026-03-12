from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import MatchRequest, Match
from chat.models import ChatRoom

User = get_user_model()


@login_required
def send_request(request):
    if request.method == "POST" and request.user.is_authenticated:
        username = request.POST.get("username")
        if not username:
            return JsonResponse(
                {"status": "error", "message": "No username provided"},
                status=400
            )

        try:
            target_user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse(
                {"status": "user_not_found", "message": "User not found"},
                status=404
            )

        if target_user == request.user:
            return JsonResponse(
                {"status": "error", "message": "Can't send request to yourself"},
                status=400
            )

        if MatchRequest.objects.filter(
            sender=request.user,
            receiver=target_user
        ).exists():
            return JsonResponse(
                {"status": "already_sent", "message": "Request already sent"},
                status=400
            )

        MatchRequest.objects.create(sender=request.user, receiver=target_user)
        return JsonResponse(
            {"status": "sent", "message": "Request sent successfully"}
        )

    return JsonResponse(
        {"status": "error", "message": "Invalid request"},
        status=400
    )


@login_required
def request_cameraman(request):
    if request.method == "POST":
        username = request.POST.get("username")
        try:
            cameraman = User.objects.get(username=username, is_cameraman=True)

            if MatchRequest.objects.filter(
                sender=request.user,
                receiver=cameraman,
                status="pending"
            ).exists():
                return JsonResponse({"status": "already_sent"})

            MatchRequest.objects.create(
                sender=request.user,
                receiver=cameraman,
                status="pending"
            )
            return JsonResponse({"status": "sent"})

        except User.DoesNotExist:
            return JsonResponse({"status": "user_not_found"})

    return JsonResponse({"status": "error", "message": "Bad method"})


@login_required
def match_requests(request):
    received = MatchRequest.objects.filter(receiver=request.user, status="pending")
    sent = MatchRequest.objects.filter(sender=request.user)

    return render(request, "matches/requests.html", {
        "received": received,
        "sent": sent,
    })


@login_required
def accept_request(request, req_id):
    req = get_object_or_404(
        MatchRequest,
        id=req_id,
        receiver=request.user
    )

    req.status = "accepted"
    req.save()

    u1, u2 = sorted([req.sender, req.receiver], key=lambda u: u.id)

    Match.objects.get_or_create(
        user1=u1,
        user2=u2
    )

    room = ChatRoom.objects.filter(
        Q(user1=u1, user2=u2) | Q(user1=u2, user2=u1)
    ).first()

    if not room:
        room = ChatRoom.objects.create(
            user1=u1,
            user2=u2
        )

    return redirect("room", room_id=room.id)


@login_required
def decline_request(request, req_id):
    req = get_object_or_404(
        MatchRequest,
        id=req_id,
        receiver=request.user
    )
    req.status = "declined"
    req.save()
    return redirect("match_requests")


@login_required
def active_matches(request):
    matches = (
        MatchRequest.objects.filter(status="accepted", sender=request.user) |
        MatchRequest.objects.filter(status="accepted", receiver=request.user)
    ).distinct()

    matches_with_other = []

    for match in matches:
        other_user = match.receiver if match.sender == request.user else match.sender

        room = ChatRoom.objects.filter(
            Q(user1=request.user, user2=other_user) |
            Q(user1=other_user, user2=request.user)
        ).first()

        matches_with_other.append({
            "match": match,
            "other_user": other_user,
            "room": room,
        })

    return render(request, "matches/active.html", {
        "matches": matches_with_other
    })


@login_required
def remove_match(request, match_id):
    match_request = get_object_or_404(
        MatchRequest,
        id=match_id,
        status="accepted"
    )

    if request.user != match_request.sender and request.user != match_request.receiver:
        return JsonResponse({"error": "Not allowed"}, status=403)

    u1, u2 = sorted(
        [match_request.sender, match_request.receiver],
        key=lambda u: u.id
    )

    # delete Match table entry
    Match.objects.filter(
        Q(user1=u1, user2=u2) | Q(user1=u2, user2=u1)
    ).delete()

    # delete chat room between these users
    ChatRoom.objects.filter(
        Q(user1=u1, user2=u2) | Q(user1=u2, user2=u1)
    ).delete()

    # delete accepted request entry
    match_request.delete()

    return redirect("active_matches")