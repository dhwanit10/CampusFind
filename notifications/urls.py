from django.urls import path

from . import views

urlpatterns = [
    path("", views.notifications_dropdown, name="notifications"),
    path("read/", views.mark_all_read, name="notifications-read"),
]