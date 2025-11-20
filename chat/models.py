from django.db import models

class ChatMessage(models.Model):
    from_user = models.ForeignKey('accounts.CustomUser', related_name='sent_messages', on_delete=models.CASCADE)
    to_user = models.ForeignKey('accounts.CustomUser', related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"From {self.from_user.username} to {self.to_user.username}: {self.content[:20]}"
