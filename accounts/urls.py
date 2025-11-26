from django.urls import path
from . import views
from django.urls import path
from .views import register, login_view, feedback_and_logout, profile

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout-review/', feedback_and_logout, name='feedback_and_logout'),
    path('profile/', profile, name='profile'),
    

]
