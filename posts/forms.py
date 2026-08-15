from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Post, Comment, Campus


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
        fields = ["bio", "profile_image", "campus"]

        widgets = {
            "bio": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    "placeholder": "Write something about yourself..."
                }
            ),
            "campus": forms.Select(
                attrs={
                    "class": "form-select",
                    "id": "campus-select"
                }
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make sure campus field shows all campuses
        self.fields['campus'].queryset = Campus.objects.all().order_by('name')
        self.fields['campus'].empty_label = "Select your campus..."
        self.fields['campus'].required = False

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