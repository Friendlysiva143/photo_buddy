from django.shortcuts import render,redirect
from django.core.mail import send_mail
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.contrib import messages
from .forms import EditProfileForm
from django.core.mail import send_mail
from django.contrib import messages
import smtplib


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



def settings_page(request):
    profile_form = EditProfileForm(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)

    if request.method == "POST":
        if 'send_message' in request.POST:
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            user_email = request.user.email
            try:
                send_mail(
                    subject,
                    message,
                    user_email,
                    ['photobuddy001@gmail.com'],
                    fail_silently=False,
                )
                messages.success(request, 'Your message has been sent!')
            except smtplib.SMTPException as e:
                messages.error(request, f'Mail failed to send: {e}')
                # optionally log the error or print(e)
            messages.success(request, 'Your message has been sent!')
            return redirect('settings')

        elif 'delete_account' in request.POST:
            request.user.delete()
            messages.success(request, 'Your account has been deleted.')
            return redirect('home')

        elif 'edit_profile' in request.POST:
            profile_form = EditProfileForm(request.POST, request.FILES, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Your profile has been updated!')
                return redirect('settings')
            else:
                messages.error(request, 'Please correct errors in your profile.')

        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully changed!')
                return redirect('settings')
            else:
                messages.error(request, 'Please correct errors in your password.')
    
    context = {
        'profile_form': profile_form,
        'password_form': password_form,
    }
    return render(request, 'auth/settings.html', context)