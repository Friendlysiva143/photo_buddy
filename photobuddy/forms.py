from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'gender', 'bio', 'profile_picture', 'is_cameraman']

        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'gender': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
