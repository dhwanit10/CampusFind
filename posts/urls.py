from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
# posts/urls.py
urlpatterns = [
    path("", views.home, name="home"),
    path("profile/", views.profile_view, name='profile'),
    path('user/<str:username>/', views.user_profile, name='userprofile'),
    path("profile/edit/", views.edit_profile, name="edit-profile"),
    path("post/create/", views.create_post, name="create-post"),
    path("post/<int:post_id>/delete/", views.delete_post, name="delete-post"),
    path("post/<int:post_id>/edit/", views.edit_post, name="edit-post"),
    path("post/<int:post_id>/like/", views.toggle_like, name="toggle-like"),
    path("post/<int:post_id>/comment/", views.add_comment, name="add-comment"),
    path("user/<str:username>/follow/", views.toggle_follow, name="toggle-follow")
] 