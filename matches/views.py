from django.shortcuts import render

# Create your views here.
def active_matches(request):
    # Query for user's active matches
    return render(request, 'matches/active.html', { 'active_matches': [...] })

def match_requests(request):
    # Query for user's match requests
    return render(request, 'matches/requests.html', { 'match_requests': [...] })
