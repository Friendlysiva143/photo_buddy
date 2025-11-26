from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import MatchRequest, Match
from chat.models import ChatRoom
from django.contrib.auth import get_user_model
User = get_user_model()

@login_required
def send_request(request):
    if request.method == "POST" and request.user.is_authenticated:
        username = request.POST.get('username')
        if not username:
            return JsonResponse({'status': 'error', 'message': 'No username provided'}, status=400)
        try:
            target_user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'status': 'user_not_found', 'message': 'User not found'}, status=404)
        if target_user == request.user:
            return JsonResponse({'status': 'error', 'message': "Can't send request to yourself"}, status=400)
        if MatchRequest.objects.filter(sender=request.user, receiver=target_user).exists():
            return JsonResponse({'status': 'already_sent', 'message': 'Request already sent'}, status=400)
        MatchRequest.objects.create(sender=request.user, receiver=target_user)
        return JsonResponse({'status': 'sent', 'message': 'Request sent successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def request_cameraman(request):
    if request.method == "POST":
        username = request.POST.get("username")
        try:
            cameraman = User.objects.get(username=username, is_cameraman=True)
            # [Optional: create CameramanRequest object, send notification/message, etc.]
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
    req = get_object_or_404(MatchRequest, id=req_id, receiver=request.user)
    req.status = "accepted"
    req.save()
    Match.objects.create(user1=req.sender, user2=req.receiver)
    room = ChatRoom.objects.create(user1=req.sender, user2=req.receiver)
    return redirect("chat_room", room_id=room.id)

@login_required
def decline_request(request, req_id):
    req = get_object_or_404(MatchRequest, id=req_id, receiver=request.user)
    req.status = "declined"
    req.save()
    return redirect("match_requests")

@login_required
def active_matches(request):
    matches = MatchRequest.objects.filter(status='accepted').filter(sender=request.user) | \
              MatchRequest.objects.filter(status='accepted').filter(receiver=request.user)
    matches_with_other = []
    for match in matches:
        other_user = match.receiver if match.sender == request.user else match.sender
        matches_with_other.append({'match': match, 'other_user': other_user})
    return render(request, 'matches/active.html', {'matches': matches_with_other})
