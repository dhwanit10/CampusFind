from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Story(models.Model):
    """A 24-hour disappearing post shown in the strip at the top of the feed."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="stories",
    )
    image = models.ImageField(upload_to="stories/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "stories"

    def __str__(self):
        return f"Story by {self.user.username}"

    @property
    def is_expired(self) -> bool:
        return timezone.now() - self.created_at > timedelta(hours=24)

    @property
    def image_url(self) -> str:
        return self.image.url if self.image else ""