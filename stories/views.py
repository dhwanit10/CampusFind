from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import Story


@login_required
def create_story(request):
    """Upload a new story image and bounce back to the home feed."""
    if request.method == "POST" and request.FILES.get("image"):
        Story.objects.create(user=request.user, image=request.FILES["image"])
    return redirect("home")


@login_required
def stories_strip(request):
    """Render the stories-strip partial with the latest story per user."""
    cutoff = timezone.now() - timedelta(hours=24)
    recent = (
        Story.objects.filter(created_at__gte=cutoff)
        .select_related("user", "user__profile")
        .order_by("-created_at")
    )

    seen: set[int] = set()
    unique = []
    for s in recent:
        if s.user_id in seen:
            continue
        seen.add(s.user_id)
        unique.append(s)

    return render(
        request,
        "stories/components/stories_strip.html",
        {"stories": unique},
    )