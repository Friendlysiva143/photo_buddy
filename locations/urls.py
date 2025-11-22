from django.urls import path
from . import views

urlpatterns = [
    path('update-location/', views.update_location, name='update_location'),
    path('nearby-users-json/', views.nearby_users, name='nearby_users_json'),
]
