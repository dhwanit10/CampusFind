from django.urls import re_path
from .consumers import PostConsumer

websocket_urlpatterns = [
    re_path(r"ws/posts/(?P<post_id>\d+)/$", PostConsumer.as_asgi()),
]
