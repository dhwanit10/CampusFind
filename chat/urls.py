from django.urls import path
from . import views

urlpatterns = [
    path("", views.inbox, name="inbox"),
    path("<int:conversation_id>/", views.conversation, name="conversation"),
    path("start/<str:username>/", views.start_chat, name="start-chat"),
    path("<int:conversation_id>/send/", views.send_message, name="send-message")
]