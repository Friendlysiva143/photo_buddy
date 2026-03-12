from django.urls import path
from . import views
from locations.views import nearby_users

urlpatterns = [
    path("send-request/", views.send_request, name="send_request"),
    path("requests/", views.match_requests, name="match_requests"),
    path("accept/<int:req_id>/", views.accept_request, name="accept_request"),
    path("decline/<int:req_id>/", views.decline_request, name="decline_request"),
    path("active/", views.active_matches, name="active_matches"),
    path("remove/<int:match_id>/", views.remove_match, name="remove_match"),
    path("request_cameraman/", views.request_cameraman, name="request_cameraman"),
    path("locations/nearby-users-json/", nearby_users, name="nearby_users_json"),
]