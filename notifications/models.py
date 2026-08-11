from django.contrib.auth.models import User
from django.db import models

from posts.models import Comment, Post


class Notification(models.Model):
    LIKE = "like"
    COMMENT = "comment"
    FOLLOW = "follow"
    MESSAGE = "message"

    TYPE_CHOICES = [
        (LIKE, "Like"),
        (COMMENT, "Comment"),
        (FOLLOW, "Follow"),
        (MESSAGE, "Message"),
    ]

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="actions",
    )
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    post = models.ForeignKey(
        Post,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    comment = models.ForeignKey(
        Comment,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.actor} {self.type} → {self.recipient}"

    @property
    def verb(self) -> str:
        return {
            self.LIKE: "liked your post",
            self.COMMENT: "commented on your post",
            self.FOLLOW: "started following you",
            self.MESSAGE: "sent you a message",
        }.get(self.type, "interacted with you")

    @property
    def icon(self) -> str:
        return {
            self.LIKE: "bi-heart-fill text-danger",
            self.COMMENT: "bi-chat-left-text text-peach",
            self.FOLLOW: "bi-person-plus text-peach",
            self.MESSAGE: "bi-envelope-fill text-peach",
        }.get(self.type, "bi-bell text-peach")