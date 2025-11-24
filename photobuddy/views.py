from django.shortcuts import render
from django.contrib.auth import get_user_model
User = get_user_model()
def home(request):
    total_users = User.objects.count()
    return render(request, "index.html", {"total_users": total_users})

def about(request):
    return render(request, 'about.html')

def safety(request):
    return render(request, 'safety.html')

def terms(request):
    return render(request, 'terms.html')

def privacy(request):
    return render(request, 'privacy.html')
