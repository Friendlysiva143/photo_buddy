from django.urls import path
from .views import active_matches, match_requests

urlpatterns = [
    path('matches/active/', active_matches, name='active_matches'),
    path('matches/requests/', match_requests, name='match_requests'),
]
