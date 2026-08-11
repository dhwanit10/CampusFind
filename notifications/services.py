"""Single entry point for creating notifications.

Callers pass the recipient, actor, and the type. The helper:

* Skips self-actions (actor == recipient).
* Persists a Notification row.
* Pushes a `notify` event to the recipient's channel-layer group so the
  bell-icon badge updates in real time without a page reload.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Notification

logger = logging.getLogger(__name__)

VALID_TYPES = {Notification.LIKE, Notification.COMMENT, Notification.FOLLOW, Notification.MESSAGE}


def create_notification(
    *,
    recipient,
    actor,
    type_: str,
    post=None,
    comment=None,
) -> Optional[Notification]:
    if recipient is None or actor is None:
        return None
    if recipient.pk == actor.pk:
        return None
    if type_ not in VALID_TYPES:
        return None

    notif = Notification.objects.create(
        recipient=recipient,
        actor=actor,
        type=type_,
        post=post,
        comment=comment,
    )

    payload = _serialize(notif)

    try:
        layer = get_channel_layer()
        if layer is not None:
            async_to_sync(layer.group_send)(
                f"user_{recipient.id}",
                {"type": "notify", "payload": payload},
            )
    except Exception as exc:  # noqa: BLE001 — never let WS errors break a view
        logger.warning("Failed to push notification to channel layer: %s", exc)

    return notif


def _serialize(notif: Notification) -> dict[str, Any]:
    return {
        "id": notif.id,
        "type": notif.type,
        "verb": notif.verb,
        "icon": notif.icon,
        "actor_username": notif.actor.username,
        "actor_profile_image": (
            notif.actor.profile.profile_image.url
            if hasattr(notif.actor, "profile") and notif.actor.profile.profile_image
            else ""
        ),
        "post_id": notif.post_id,
        "comment_id": notif.comment_id,
        "is_read": notif.is_read,
        "created_at": notif.created_at.strftime("%b %d, %I:%M %p"),
    }