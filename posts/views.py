from django.shortcuts import render, get_object_or_404, redirect
from .models import UserProfile, Post, Like, Comment, Follow
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import UserForm, UserProfileForm, PostForm, CommentForm
from django.conf import settings
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.db.models import Count

# Create your views here.
#posts/views.py
@login_required
def home(request):
    posts = Post.objects.select_related(
        "user",
        "user__profile"
    ).prefetch_related(
        "likes",
         "comments",
    "comments__user"
    ).annotate(
        comment_count=Count("comments")
    ).order_by(
        "-created_at"
    )

    for post in posts:
        post.is_liked = post.likes.filter(
            user=request.user
        ).exists()
    return render(request, "posts/home.html", {
        'posts': posts,
        "comment_form": CommentForm()
    })

@login_required
def profile_view(request):
    posts = request.user.posts.all().prefetch_related(
            "likes",
            "comments",
            "comments__user"
        ).annotate(
            comment_count=Count("comments")
        ).order_by(
            "-created_at"
        )
    for post in posts:
            post.is_liked = post.likes.filter(
                user=request.user
            ).exists()

    followers_count = Follow.objects.filter(
        following=request.user
    ).count()
    
    following_count = Follow.objects.filter(
        follower=request.user
    ).count()

    context ={
        "profile_user":request.user,
        "profile" : request.user.profile,
        "posts": posts,
        "followers_count": followers_count,
        "following_count": following_count,
        "comment_form": CommentForm(),
    } 
    
    return render(request, "posts/profile.html", context)

@login_required
def user_profile(request, username):
    profile_user = get_object_or_404(
        User,
        username=username
    )

    posts = profile_user.posts.all().order_by(
        "-created_at"
    )
    is_following = Follow.objects.filter(
        follower=request.user,
        following=profile_user
    ).exists()
    
    followers_count = Follow.objects.filter(
        following=profile_user
    ).count()
    
    following_count = Follow.objects.filter(
        follower=profile_user
    ).count()

    context={

        "profile_user":profile_user,

        "profile":profile_user.profile,

        "posts":posts,
        "is_following": is_following,

        "followers_count": followers_count,

        "following_count": following_count,

    }

    return render(
        request,
        "posts/profile.html",
        context
    )

@login_required
def edit_profile(request):

    user = request.user
    profile = user.profile

    if request.method == "POST":

        user_form = UserForm(
            request.POST,
            instance=user
        )

        profile_form = UserProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if user_form.is_valid() and profile_form.is_valid():

            user_form.save()

            profile = profile_form.save(commit=False)


            # If user selected "Remove Profile Picture"
            if request.POST.get("remove_image") == "1":
                profile.profile_image = "profile_images/default.png"

            profile.save()

            return redirect("profile")

    else:

        user_form = UserForm(instance=user)

        profile_form = UserProfileForm(instance=profile)

    context = {

        "user_form": user_form,

        "profile_form": profile_form,

        "default_profile_image": settings.MEDIA_URL + "profile_images/default.png",

    }

    return render(request, "posts/edit_profile.html", context)

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()

            return redirect("home")
        
    else:
        form = PostForm()

    return render(request, "posts/create_post.html", {'form': form})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.user != request.user:
        return HttpResponseForbidden('You are not allowed to delete this post.')

    if request.method == 'POST':

        next_url = request.POST.get("next")
        post.delete()

        messages.success(
            request, 
            "Post deleted successfully."
        )
        if next_url:
            return redirect(next_url)

        return redirect("home")

    return redirect("home")

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.user != request.user:
        return HttpResponseForbidden(
            "You are not allowed to edit this post."
        )

    if request.method == "POST":
        form = PostForm(
            request.POST,
            request.FILES,
            instance=post
        )

        if form.is_valid():
            form.save()

            messages.success(
                request, 
                "Post updated successfully."
            )

            next_url = request.POST.get("next")

            if next_url:
                return redirect(next_url)

            return redirect("home")
        
    else:
        form = PostForm(instance=post)

    return render(
        request, 
        "posts/edit_post.html", 
        {
        'form' : form,
        'post' : post,
        }
    )


@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id
    )

    like = Like.objects.filter(
        user=request.user,
        post=post
    )

    if like.exists():
        like.delete()

    else:
        Like.objects.create(
            user=request.user,
            post=post
        )

    next_url = request.POST.get("next")

    if next_url:
        return redirect(next_url)

    return redirect("home")

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id
    )

    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()

            messages.success(
                request, "Comment added."
            )

        next_url = request.POST.get("next")

        if next_url:
            return redirect(next_url)

        return redirect("home")

def toggle_follow(request, username):
    user_to_follow = get_object_or_404(
        User,
        username = username
    )
    if user_to_follow == request.user:
        return HttpResponseForbidden("you cannot follow yourself.")

    follow = Follow.objects.filter(
        follower=request.user,
        following= user_to_follow
    )

    if follow.exists():
        follow.delete()
        messages.success(
            request,
            f"you unfollowed {user_to_follow.username}."
        )
    else:
        Follow.objects.create(
            follower=request.user,
            following=user_to_follow
        )

        messages.success(
            request,
            f"you are now following {user_to_follow.username}"
        )

    next_url = request.POST.get("next")

    if next_url:
        return redirect(next_url)

    return redirect("userprofile", username=username)