from datetime import timedelta

from django import template
from django.utils import timezone

from stories.models import Story

register = template.Library()


@register.inclusion_tag("stories/components/stories_strip.html", takes_context=True)
def render_stories_strip(context):
    request = context["request"]
    cutoff = timezone.now() - timedelta(hours=24)
    recent = (
        Story.objects.filter(created_at__gte=cutoff)
        .select_related("user", "user__profile")
        .order_by("-created_at")
    )

    seen = set()
    unique = []
    for s in recent:
        if s.user_id in seen:
            continue
        seen.add(s.user_id)
        unique.append(s)

    return {
        "stories": unique,
        "request": request,
    }