from django.urls import path
from . import views

urlpatterns = [
    path("active/", views.active_matches, name="active_matches"),
    path("requests/", views.match_requests, name="match_requests"),
    path("<int:id>/accept/", views.accept_match, name="accept_match"),
    path("<int:id>/decline/", views.decline_match, name="decline_match"),
]
