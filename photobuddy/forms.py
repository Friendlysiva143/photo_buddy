from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email','bio','profile_picture']  # Add fields as needed for your custom model
