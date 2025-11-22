# matches/models.py

from django.conf import settings
from django.db import models

class MatchRequest(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='sent_requests',
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_requests',
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=10,
        choices=(
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('declined', 'Declined'),
        ),
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender} → {self.receiver} ({self.status})"


class Match(models.Model):
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="match_user1"
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="match_user2"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Match: {self.user1} & {self.user2}"
