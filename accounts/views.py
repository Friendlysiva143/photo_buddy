from django.shortcuts import render, redirect
from .models import CustomUser
from django.contrib import messages
from django.db.models import Q
import hashlib

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        raw_password = request.POST.get('password')
        bio = request.POST.get('bio', '')
        profile_picture = request.FILES.get('profile_picture')

        # Simple validations
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return render(request, 'auth/register.html')
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return render(request, 'auth/register.html')
        if len(raw_password) < 6:
            messages.error(request, 'Password is too short!')
            return render(request, 'auth/register.html')

        hashed_password = hashlib.sha256(raw_password.encode()).hexdigest()

        user = CustomUser(username=username, email=email, password=hashed_password, bio=bio)
        if profile_picture:
            user.profile_picture = profile_picture
        user.save()
        messages.success(request, 'Registration successful! Please log in.')
        return redirect('login')
    return render(request, 'auth/register.html')



def login(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        raw_password = request.POST.get('password')
        hashed_password = hashlib.sha256(raw_password.encode()).hexdigest()

        # Try to find user by username or email, and password
        user = CustomUser.objects.filter(
            Q(username=username_or_email) | Q(email=username_or_email),
            password=hashed_password
        ).first()
        if user:
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            messages.success(request, f"Welcome, {user.username}!")
            return redirect('/')
        else:
            messages.error(request, 'Invalid credentials!')
            return render(request, 'auth/login.html')
    return render(request, 'auth/login.html')


def profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    user = CustomUser.objects.get(id=user_id)
    return render(request, 'auth/profile.html', {'user': user})

def logout(request):
    request.session.flush()
    messages.success(request, 'Logged out!')
    return redirect('login')


def edit_profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    user = CustomUser.objects.get(id=user_id)
    profile = user  # For simple structure; adjust if you add a separate Profile model

    if request.method == 'POST':
        remove_pic = request.POST.get('remove_picture')
        
        # 1. Remove Profile Picture
        if remove_pic == "yes":
            if profile.profile_picture:
                profile.profile_picture.delete(save=False)  # Delete file from disk
                profile.profile_picture = None
                profile.save()
            messages.success(request, 'Profile picture removed!')
            return redirect('edit_profile')

        # 2. Update other profile fields
        username = request.POST.get('username').strip()
        bio = request.POST.get('bio')
        profile_picture = request.FILES.get('profile_picture')

        if username != user.username and CustomUser.objects.filter(username=username).exclude(id=user_id).exists():
            messages.error(request, 'This username is already taken!')
            return render(request, 'auth/edit_profile.html', {'user': user, 'profile': profile})

        user.username = username
        user.bio = bio
        if profile_picture:
            user.profile_picture = profile_picture
        user.save()
        messages.success(request, 'Your profile was updated!')
        return redirect('profile')

    # For GET request (page load), just show the form
    return render(request, 'auth/edit_profile.html', {'user': user, 'profile': profile})
