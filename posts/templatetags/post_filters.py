from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def instagram_date(value):

    now = timezone.now()

    diff = now - value

    seconds = diff.total_seconds()

    if seconds < 60:
        return "Just now"

    elif seconds < 3600:

        minutes = int(seconds // 60)

        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"

    elif seconds < 86400:

        hours = int(seconds // 3600)

        return f"{hours} hour{'s' if hours != 1 else ''} ago"

    else:

        return value.strftime("%d %B %Y")