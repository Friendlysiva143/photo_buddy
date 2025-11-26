from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout as django_logout
from .models import CustomUser
from .forms import UserReviewForm   # If you have a review form

# Registration form with extra fields
class CustomUserCreationForm(UserCreationForm):
    bio = forms.CharField(required=False, widget=forms.Textarea)
    profile_picture = forms.ImageField(required=False)
    is_cameraman = forms.BooleanField(label='Register as Professional Cameraman', required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'bio', 'profile_picture', 'is_cameraman')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.bio = self.cleaned_data.get('bio', "")
        if self.cleaned_data.get('profile_picture'):
            user.profile_picture = self.cleaned_data['profile_picture']
        user.is_cameraman = self.cleaned_data.get('is_cameraman', False)
        if commit:
            user.save()
        return user

# Register view
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

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, "Invalid credentials!")
    return render(request, 'auth/login.html')

# Profile view
@login_required
def profile(request):
    return render(request, 'auth/profile.html', {'user': request.user})

# Feedback and logout view
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
            return redirect('login')
    else:
        form = UserReviewForm()
    return render(request, 'feedback/review_before_logout.html', {'form': form})