from django.urls import path
from . import views

urlpatterns = [
    path('active/', views.active_matches, name='active_matches'),
    path('requests/', views.match_requests, name='match_requests'),

    # send a request (from map)
    path('send/<int:user_id>/', views.send_match_request, name='send_match_request'),

    # accept / decline
    path('accept/<int:request_id>/', views.accept_match, name='accept_match'),
    path('decline/<int:request_id>/', views.decline_match, name='decline_match'),

    path('request/', views.send_match_request_api, name='send_match_request_api'),

]
