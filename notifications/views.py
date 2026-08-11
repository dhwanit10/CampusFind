from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import Notification


@login_required
def notifications_dropdown(request):
    """Render the dropdown partial used by the bell icon in the navbar."""
    items = (
        Notification.objects
        .filter(recipient=request.user)
        .select_related("actor", "actor__profile", "post")[:15]
    )
    unread = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return render(
        request,
        "notifications/components/dropdown.html",
        {"items": items, "unread": unread},
    )


@login_required
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect(request.META.get("HTTP_REFERER") or "home")