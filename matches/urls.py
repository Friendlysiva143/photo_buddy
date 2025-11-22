from django.urls import path
from . import views

urlpatterns = [
   path('request/', views.send_request, name='send_request'),
    path('incoming/', views.incoming_requests, name='incoming_requests'),
    path('respond/', views.respond_request, name='respond_request'),
]
