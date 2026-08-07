from django.db import models
from django.contrib.auth.models import User


class Conversation(models.Model):
    participants = models.ManyToManyField(
        User,
        related_name="conversations"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
    def __str__(self):
        return ", ".join(
            user.username
            for user in self.participants.all()
        )

class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender.username}: {self.content[:25]}"


class ConversationStatus(models.Model):

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="statuses"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    unread_count = models.PositiveIntegerField(
        default=0
    )

    class Meta:

        unique_together = (
            "conversation",
            "user",
        )

    def __str__(self):
        return f"{self.user.username} - {self.unread_count}"
