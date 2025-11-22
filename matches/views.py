from django.shortcuts import render

# Create your views here.
def active_matches(request):
    # Query for user's active matches
    return render(request, 'matches/active.html', { 'active_matches': [...] })

def match_requests(request):
    # Query for user's match requests
    return render(request, 'matches/requests.html', { 'match_requests': [...] })
from django.shortcuts import redirect

def accept_match(request, id):
    if request.method == "POST":
        # your accept logic here
        # match = Match.objects.get(id=id)
        # match.status = 'accepted'
        # match.save()

        return redirect('demo_chat')   # 👈 go to demo_chat page

    return redirect('demo_chat')
def decline_match(request, id):
    if request.method == "POST":
        # your decline logic here
        # match = Match.objects.get(id=id)
        # match.status = 'declined'
        # match.save()

        return redirect('home')   # 👈 go to home page

    return redirect('home')
