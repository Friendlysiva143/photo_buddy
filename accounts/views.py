from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django import forms
from django.contrib.auth.decorators import login_required
from .forms import UserReviewForm
from django.contrib.auth import logout as django_logout


# Extend UserCreationForm to include custom fields (bio/profile_picture)
class CustomUserCreationForm(UserCreationForm):
    bio = forms.CharField(required=False, widget=forms.Textarea)
    profile_picture = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'bio', 'profile_picture')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/register.html', {'form': form})

from django.contrib.auth import authenticate, login

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')    # Must match the form field name!
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, "Invalid credentials!")
    return render(request, 'auth/login.html')


@login_required
def feedback_and_logout(request):
    if request.method == 'POST':
        form = UserReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            messages.success(request, "Thanks for your feedback!")
            django_logout(request)
            return redirect('login')  # Or your homepage
    else:
        form = UserReviewForm()
    return render(request, 'feedback/review_before_logout.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'auth/profile.html', {'user': request.user})

