from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import MatchRequest

@login_required
def send_request(request):
    if request.method == "POST":
        receiver_username = request.POST.get('username')
        try:
            receiver = User.objects.get(username=receiver_username)
            match_request, created = MatchRequest.objects.get_or_create(
                sender=request.user, receiver=receiver
            )
            if created:
                return JsonResponse({'status': 'sent'})
            else:
                return JsonResponse({'status': 'already_sent'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'user_not_found'})
    return JsonResponse({'status': 'invalid'})


@login_required
def incoming_requests(request):
    requests = MatchRequest.objects.filter(receiver=request.user, status='pending')
    data = [
        {'id': r.id, 'sender': r.sender.username, 'created_at': r.created_at.strftime('%Y-%m-%d %H:%M')}
        for r in requests
    ]
    return JsonResponse(data, safe=False)


@login_required
def respond_request(request):
    if request.method == "POST":
        req_id = request.POST.get('request_id')
        action = request.POST.get('action')  # "accept" or "decline"
        try:
            match_request = MatchRequest.objects.get(id=req_id, receiver=request.user)
            if action == 'accept':
                match_request.status = 'accepted'
            elif action == 'decline':
                match_request.status = 'declined'
            match_request.save()
            return JsonResponse({'status': 'success', 'action': action})
        except MatchRequest.DoesNotExist:
            return JsonResponse({'status': 'not_found'})
    return JsonResponse({'status': 'invalid'})
