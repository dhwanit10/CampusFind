from .models import Notification


def unread_count(request):
    """Inject the unread notification count into every template context."""
    if request.user.is_authenticated:
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return {"unread_count": count, "unread_notifications": count}
    return {"unread_count": 0, "unread_notifications": 0}