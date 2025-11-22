from django.urls import path
from . import views

urlpatterns = [
    path("send/<int:user_id>/", views.send_request, name="send_request"),
    path("requests/", views.match_requests, name="match_requests"),
    path("accept/<int:req_id>/", views.accept_request, name="accept_request"),
    path("decline/<int:req_id>/", views.decline_request, name="decline_request"),
    path("active/", views.active_matches, name="active_matches"),
]
