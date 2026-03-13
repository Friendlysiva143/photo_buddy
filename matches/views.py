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
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {"status": "error", "message": "No username provided"},
                    status=400
                )
            return redirect("posts:posts_feed")

        try:
            target_user = User.objects.get(username=username)
        except User.DoesNotExist:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {"status": "user_not_found", "message": "User not found"},
                    status=404
                )
            return redirect("posts:posts_feed")

        if target_user == request.user:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {"status": "error", "message": "Can't send request to yourself"},
                    status=400
                )
            return redirect("posts:user_posts", username=username)

        if MatchRequest.objects.filter(
            sender=request.user,
            receiver=target_user
        ).exclude(status="declined").exists():
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {"status": "already_sent", "message": "Request already sent"},
                    status=400
                )
            return redirect("posts:user_posts", username=username)

        if MatchRequest.objects.filter(
            sender=target_user,
            receiver=request.user,
            status="pending"
        ).exists():
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "status": "already_received",
                        "message": "This user has already sent you a request"
                    },
                    status=400
                )
            return redirect("posts:user_posts", username=username)

        MatchRequest.objects.create(sender=request.user, receiver=target_user)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(
                {"status": "sent", "message": "Request sent successfully"}
            )

        return redirect("posts:user_posts", username=username)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse(
            {"status": "error", "message": "Invalid request"},
            status=400
        )

    return redirect("posts:posts_feed")


@login_required
def request_cameraman(request):
    if request.method == "POST":
        username = request.POST.get("username")

        try:
            cameraman = User.objects.get(username=username, is_cameraman=True)

            if cameraman == request.user:
                return JsonResponse(
                    {"status": "error", "message": "You cannot request yourself"},
                    status=400
                )

            if MatchRequest.objects.filter(
                sender=request.user,
                receiver=cameraman
            ).exclude(status="declined").exists():
                return JsonResponse({"status": "already_sent"})

            MatchRequest.objects.create(
                sender=request.user,
                receiver=cameraman,
                status="pending"
            )
            return JsonResponse({"status": "sent"})

        except User.DoesNotExist:
            return JsonResponse({"status": "user_not_found"}, status=404)

    return JsonResponse({"status": "error", "message": "Bad method"}, status=400)


@login_required
def matches_page(request):
    received = MatchRequest.objects.filter(
        receiver=request.user,
        status="pending"
    ).select_related("sender")

    sent = MatchRequest.objects.filter(
        sender=request.user
    ).select_related("receiver")

    accepted_requests = (
        MatchRequest.objects.filter(status="accepted", sender=request.user) |
        MatchRequest.objects.filter(status="accepted", receiver=request.user)
    ).select_related("sender", "receiver").distinct()

    matches_with_other = []

    for match in accepted_requests:
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

    active_tab = request.GET.get("tab", "requests")

    return render(request, "matches/matches.html", {
        "received": received,
        "sent": sent,
        "matches": matches_with_other,
        "active_tab": active_tab,
    })


@login_required
def accept_request(request, req_id):
    req = get_object_or_404(
        MatchRequest,
        id=req_id,
        receiver=request.user,
        status="pending"
    )

    sender_username = req.sender.username

    req.status = "accepted"
    req.save()

    u1, u2 = sorted([req.sender, req.receiver], key=lambda u: u.id)

    Match.objects.get_or_create(user1=u1, user2=u2)

    room = ChatRoom.objects.filter(
        Q(user1=u1, user2=u2) | Q(user1=u2, user2=u1)
    ).first()

    if not room:
        ChatRoom.objects.create(user1=u1, user2=u2)

    return redirect("posts:user_posts", username=sender_username)


@login_required
def decline_request(request, req_id):
    req = get_object_or_404(
        MatchRequest,
        id=req_id,
        receiver=request.user,
        status="pending"
    )

    sender_username = req.sender.username

    req.status = "declined"
    req.save()

    return redirect("posts:user_posts", username=sender_username)


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

    Match.objects.filter(
        Q(user1=u1, user2=u2) | Q(user1=u2, user2=u1)
    ).delete()

    ChatRoom.objects.filter(
        Q(user1=u1, user2=u2) | Q(user1=u2, user2=u1)
    ).delete()

    match_request.delete()

    return redirect("/matches/?tab=active")

@login_required
def cancel_request(request, username):
    target_user = get_object_or_404(User, username=username)

    match_request = MatchRequest.objects.filter(
        sender=request.user,
        receiver=target_user,
        status="pending"
    ).first()

    if match_request:
        match_request.delete()

    return redirect("posts:user_posts", username=username)