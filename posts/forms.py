from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Post, Comment


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]


class UserProfileForm(forms.ModelForm):
    remove_profile_image = forms.BooleanField(
        required=False,
        label="Remove Profile Picture"
    )
    class Meta:
        model = UserProfile
        fields = ["bio", "profile_image"]

        widgets = {
            "bio": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    "placeholder": "Write something about yourself..."
                }
            )
        }
class PostForm(forms.ModelForm):

    class Meta:

        model = Post

        fields = [
            "image",
            "caption"
        ]

        widgets = {

            "caption": forms.Textarea(
                attrs={
                    "rows":3,
                    "class":"form-control",
                    "placeholder":"Write a caption..."
                }
            )

        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["comment"]
        widgets = {
            "comment" : forms.Textarea(
                attrs={
                    "rows": 1,
                    "class" : "comment-input",
                    "placeholder": "Add a comment...",
                    "maxlength": 300,
                }
            )
        }