from django import forms
from .models import UserReview

class UserReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, f"{i} Stars") for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={'class': 'star-rating'})
    )
    review = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Write your feedback...', 'rows': 3}),
        required=False
    )

    class Meta:
        model = UserReview
        fields = ['rating', 'review']
