from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# project views.py
def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully.")
            return redirect("login")
        
    else:
        form = UserCreationForm()

    return render(request, "auth/signup.html", {"form": form})

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

