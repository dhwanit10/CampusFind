from django.urls import path

from . import views

urlpatterns = [
    path("create/", views.create_story, name="create-story"),
    path("strip/", views.stories_strip, name="stories-strip"),
]