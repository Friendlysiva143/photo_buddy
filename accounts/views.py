from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout as django_logout
from .models import CustomUser, UserReview
from .forms import UserReviewForm
from photos.models import Post


class CustomUserCreationForm(UserCreationForm):
    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'form-input',
        'rows': 3,
        'placeholder': 'Tell something about yourself'
    }))
    profile_picture = forms.ImageField(required=False)
    is_cameraman = forms.BooleanField(
        label='Register as Professional Cameraman',
        required=False
    )

    gender = forms.ChoiceField(
        choices=CustomUser.GENDER_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )

    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            'username',
            'email',
            'bio',
            'profile_picture',
            'gender',
            'is_cameraman',
            'password1',
            'password2',
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        user.bio = self.cleaned_data.get('bio', "")
        user.gender = self.cleaned_data.get('gender')
        user.is_cameraman = self.cleaned_data.get('is_cameraman', False)

        if self.cleaned_data.get('profile_picture'):
            user.profile_picture = self.cleaned_data['profile_picture']

        if commit:
            user.save()
        return user


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


@login_required
def profile(request):
    user_posts = Post.objects.filter(user=request.user)

    context = {
        'user': request.user,
        'posts': user_posts
    }
    return render(request, 'auth/profile.html', context)


@login_required
def feedback_and_logout(request):
    if UserReview.objects.filter(user=request.user).exists():
        django_logout(request)
        return redirect('login')

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