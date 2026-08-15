from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from posts.models import Campus, UserProfile
from django.contrib.auth.models import User

# project views.py
def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        campus_id = request.POST.get("campus")
        
        if form.is_valid():
            user = form.save()
            
            # Get the campus
            campus = None
            if campus_id:
                try:
                    campus = Campus.objects.get(id=campus_id)
                except Campus.DoesNotExist:
                    pass
            
            # Create user profile with campus
            # Check if profile already exists (from signals)
            try:
                profile = user.profile
                # If profile exists, update the campus
                profile.campus = campus
                profile.save()
            except UserProfile.DoesNotExist:
                # Create profile if it doesn't exist
                UserProfile.objects.create(
                    user=user,
                    campus=campus
                )
            
            messages.success(request, "Account created successfully!")
            return redirect("login")
        
    else:
        form = UserCreationForm()
    
    # Get all campuses for the dropdown
    campuses = Campus.objects.all().order_by('name')
    
    return render(request, "auth/signup.html", {
        "form": form,
        "campuses": campuses
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(
            request,
            username=username,
            password=password,
        )
        if user:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid credentials.")

    return render(request, "auth/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")