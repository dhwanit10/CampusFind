from django.shortcuts import render, get_object_or_404, redirect
from .models import UserProfile, Post, Like, Comment, Follow, Campus
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import UserForm, UserProfileForm, PostForm, CommentForm
from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.db.models import Count, Q
from django.db.models import Exists, OuterRef
from ai.services import suggest_captions

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

    followers = Follow.objects.filter(
        following=request.user
    ).select_related("follower", "follower__profile")

    following = Follow.objects.filter(
        follower=request.user
    ).select_related("following", "following__profile")

    context ={
        "profile_user":request.user,
        "profile" : request.user.profile,
        "posts": posts,
        "followers_count": followers_count,
        "following_count": following_count,
         "followers": followers,
        "following": following,
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

    followers = Follow.objects.filter(
        following=profile_user
    ).select_related("follower", "follower__profile")

    following = Follow.objects.filter(
        follower=profile_user
    ).select_related("following", "following__profile")

    context={

        "profile_user":profile_user,

        "profile":profile_user.profile,

        "posts":posts,
        "is_following": is_following,

        "followers_count": followers_count,

        "following_count": following_count,

        "followers": followers,
        "following": following,

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

        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

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
def campus_suggestions(request):
    """Get users from same campus who you don't follow yet"""
    if not request.user.is_authenticated:
        return JsonResponse({'suggestions': []})
    
    user_profile = request.user.profile
    suggestions = []
    
    if user_profile.campus:
        # Get users from same campus
        followed_users = Follow.objects.filter(
            follower=request.user
        ).values_list('following_id', flat=True)
        
        campus_users = UserProfile.objects.filter(
            campus=user_profile.campus
        ).exclude(
            user=request.user
        ).exclude(
            user__in=followed_users
        ).select_related('user')[:10]
        
        for profile in campus_users:
            suggestions.append({
                'username': profile.user.username,
                'profile_image': profile.profile_image.url if profile.profile_image else None,
                'bio': profile.bio[:50] if profile.bio else '',
            })
    
    return JsonResponse({'suggestions': suggestions})

# NEW: Get posts from users in your campus
@login_required
def campus_feed(request):
    """Show posts from users in the same campus"""
    user_profile = request.user.profile
    
    if not user_profile.campus:
        messages.info(request, "Set your campus to see posts from your community!")
        return redirect('home')
    
    # Get all users from same campus
    campus_users = UserProfile.objects.filter(
        campus=user_profile.campus
    ).values_list('user_id', flat=True)
    
    posts = Post.objects.filter(
        user_id__in=campus_users
    ).select_related(
        "user", "user__profile"
    ).prefetch_related(
        "likes", "comments", "comments__user"
    ).annotate(
        comment_count=Count("comments")
    ).order_by("-created_at")
    
    for post in posts:
        post.is_liked = post.likes.filter(user=request.user).exists()
    
    return render(request, "posts/campus_feed.html", {
        'posts': posts,
        'campus_name': user_profile.campus.name,
        'comment_form': CommentForm()
    })


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

        from notifications.services import create_notification
        create_notification(
            recipient=post.user,
            actor=request.user,
            type_="like",
            post=post,
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

            from notifications.services import create_notification
            create_notification(
                recipient=post.user,
                actor=request.user,
                type_="comment",
                post=post,
                comment=comment,
            )

            messages.success(
                request, "Comment added."
            )

        next_url = request.POST.get("next")

        if next_url:
            return redirect(next_url)

        return redirect("home")

@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    # Allow delete if the user is the comment author OR the post owner.
    if request.user != comment.user and request.user != comment.post.user:
        return HttpResponseForbidden("You are not allowed to delete this comment.")

    if request.method == "POST":
        next_url = request.POST.get("next")
        comment.delete()
        messages.success(request, "Comment deleted.")
        if next_url:
            return redirect(next_url)
        return redirect("home")

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

        from notifications.services import create_notification
        create_notification(
            recipient=user_to_follow,
            actor=request.user,
            type_="follow",
        )

    next_url = request.POST.get("next")

    if next_url:
        return redirect(next_url)

    return redirect("userprofile", username=username)


@login_required
def suggest_caption(request):
    """AJAX endpoint hit by the ✨ Suggest button on the create-post page."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    caption = request.POST.get("caption", "")
    result = suggest_captions(caption)
    return JsonResponse(result)


@login_required
def search_view(request):
    q = request.GET.get("q", "").strip()
    campus_filter = request.GET.get("campus", "")

    users, posts = [], []
    if q:
        users = User.objects.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        ).select_related("profile").distinct()[:20]
        
        # If campus filter is applied, filter users by campus
        if campus_filter:
            users = users.filter(profile__campus_id=campus_filter)
        
        # Fix the post search
        posts = Post.objects.filter(
            Q(caption__icontains=q) |
            Q(user__username__icontains=q)
        ).select_related("user", "user__profile").prefetch_related(
            "likes", "comments"
        ).order_by("-created_at")[:30]
        
        # If campus filter is applied, filter posts by user's campus
        if campus_filter:
            posts = posts.filter(user__profile__campus_id=campus_filter)
        
        # Add is_liked to each post
        for post in posts:
            post.is_liked = post.likes.filter(user=request.user).exists()

    campuses = Campus.objects.all().order_by('name')
    return render(
        request,
        "posts/search.html",
        {
            "q": q,
            "users": users,
            "posts": posts,
            "campuses": campuses,
            "selected_campus": campus_filter
        },
    )

