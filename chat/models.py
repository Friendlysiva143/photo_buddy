from django.conf import settings
from django.db import models


class ChatRoom(models.Model):
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_user1'
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_user2'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat between {self.user1} and {self.user2}"


class Message(models.Model):
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )

    text = models.TextField(blank=True, null=True)

    image = models.ImageField(
        upload_to="chat_images/",
        blank=True,
        null=True
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.text:
            return f"{self.sender}: {self.text[:20]}"
        return f"{self.sender}: Image"


class Call(models.Model):
    CALL_TYPES = (
        ("voice", "Voice"),
        ("video", "Video"),
    )

    STATUS_CHOICES = (
        ("calling", "Calling"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
        ("ended", "Ended"),
        ("missed", "Missed"),
    )

    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="calls"
    )

    caller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="calls_made"
    )

    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="calls_received"
    )

    call_type = models.CharField(max_length=10, choices=CALL_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="calling")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.caller} -> {self.receiver} ({self.call_type}, {self.status})"