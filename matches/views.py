from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User

from .models import MatchRequest, Match
from chat.models import ChatRoom


# -----------------------------
# SEND REQUEST
# -----------------------------
@login_required
def send_request(request, user_id):
    receiver = get_object_or_404(User, id=user_id)

    # Prevent duplicate requests
    if MatchRequest.objects.filter(sender=request.user, receiver=receiver, status="pending").exists():
        return JsonResponse({'status': 'already_sent'})

    MatchRequest.objects.create(sender=request.user, receiver=receiver)
    return JsonResponse({'status': 'sent'})
    

# -----------------------------
# SHOW REQUESTS (sent + received)
# -----------------------------
@login_required
def match_requests(request):
    received = MatchRequest.objects.filter(receiver=request.user, status="pending")
    sent = MatchRequest.objects.filter(sender=request.user)

    return render(request, "matches/requests.html", {
        "received": received,
        "sent": sent,
    })


# -----------------------------
# ACCEPT REQUEST
# -----------------------------
@login_required
def accept_request(request, req_id):
    req = get_object_or_404(MatchRequest, id=req_id, receiver=request.user)

    # Mark as accepted
    req.status = "accepted"
    req.save()

    # Create a Match entry
    Match.objects.create(user1=req.sender, user2=req.receiver)

    # Create ChatRoom after match is accepted
    room = ChatRoom.objects.create(
        user1=req.sender,
        user2=req.receiver
    )

    # Redirect using URL name — IMPORTANT
    return redirect("chat_room", room_id=room.id)


# -----------------------------
# DECLINE REQUEST
# -----------------------------
@login_required
def decline_request(request, req_id):
    req = get_object_or_404(MatchRequest, id=req_id, receiver=request.user)

    req.status = "declined"
    req.save()

    return redirect("match_requests")


# -----------------------------
# ACTIVE MATCHES
# -----------------------------
@login_required
def active_matches(request):
    # Get all accepted matches for the current user
    matches = MatchRequest.objects.filter(
        status='accepted'
    ).filter(
        sender=request.user
    ) | MatchRequest.objects.filter(
        status='accepted'
    ).filter(
        receiver=request.user
    )

    # Prepare list of matches with 'other_user' for template
    matches_with_other = []
    for match in matches:
        other_user = match.receiver if match.sender == request.user else match.sender
        matches_with_other.append({'match': match, 'other_user': other_user})

    return render(request, 'matches/active.html', {'matches': matches_with_other})
