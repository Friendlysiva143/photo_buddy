from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import MatchRequest
from django.http import JsonResponse


@login_required
def send_match_request(request, user_id):
    receiver = get_object_or_404(User, id=user_id)

    # Avoid sending request to self
    if receiver == request.user:
        return redirect('active_matches')

    # Avoid duplicates
    existing = MatchRequest.objects.filter(sender=request.user, receiver=receiver, status='pending')
    if existing.exists():
        return redirect('active_matches')

    MatchRequest.objects.create(sender=request.user, receiver=receiver)
    
    return redirect('active_matches')


@login_required
def match_requests(request):
    # Incoming requests (others sending to me)
    incoming = MatchRequest.objects.filter(receiver=request.user, status='pending')

    return render(request, 'matches/requests.html', {
        'match_requests': incoming
    })


@login_required
def active_matches(request):
    # Sent requests
    sent = MatchRequest.objects.filter(sender=request.user)

    return render(request, 'matches/active.html', {
        'active_matches': sent
    })


@login_required
def accept_match(request, request_id):
    match_request = get_object_or_404(MatchRequest, id=request_id, receiver=request.user)
    match_request.status = "accepted"
    match_request.save()
    return redirect('match_requests')


@login_required
def decline_match(request, request_id):
    match_request = get_object_or_404(MatchRequest, id=request_id, receiver=request.user)
    match_request.status = "declined"
    match_request.save()
    return redirect('match_requests')

@login_required
def send_match_request_api(request):
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

    username = request.POST.get("username").strip()
    receiver = User.objects.filter(username=username).first()

    if receiver is None:
        return JsonResponse({'status': 'error', 'message': 'User not found'})

    if receiver == request.user:
        return JsonResponse({'status': 'error', 'message': 'Cannot send request to yourself'})

    # Prevent duplicate pending requests  
    existing = MatchRequest.objects.filter(
        sender=request.user,
        receiver=receiver,
        status="pending"
    )

    if existing.exists():
        return JsonResponse({'status': 'exists', 'message': 'Request already sent'})

    # Create match request
    MatchRequest.objects.create(
        sender=request.user,
        receiver=receiver,
        status="pending"
    )

    return JsonResponse({'status': 'success', 'message': 'Request sent'})