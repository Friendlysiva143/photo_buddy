from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    """Form for creating/updating posts"""
    
    class Meta:
        model = Post
        fields = ['image', 'caption','style']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'required': True,
            }),
            'caption': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write a caption for your photo...',
                'rows': 4,
                'maxlength': 2000,
            }),
        }
        labels = {
            'image': 'Upload Photo',
            'caption': 'Caption',
        }


class CommentForm(forms.ModelForm):
    """Form for adding comments to posts"""
    
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Add a comment...',
                'maxlength': 500,
            }),
        }
        labels = {
            'text': '',
        }