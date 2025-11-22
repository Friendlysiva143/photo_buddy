# matches/models.py

from django.conf import settings
from django.db import models

class MatchRequest(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # dynamically reference user model
        related_name='sent_requests',
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # dynamically reference user model
        related_name='received_requests',
        on_delete=models.CASCADE
    )
    status = models.CharField(max_length=10, choices=(
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ), default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')
