from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, reverse
from .forms import LoginUserForm, RegisterUserForm
from django.contrib import messages


def login_user(request):
    if request.method == "POST":
        form = LoginUserForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd["username"], password=cd["password"])
            if user and user.is_active:
                login(request, user)
                messages.success(request, f"You are now logged in as {user.username}")
                return HttpResponseRedirect(reverse("main_menu"))
            else:
                messages.error(request, "Invalid username or password")
    else:
        form = LoginUserForm()

    return render(request, "users/login.html", {"form": form})


def register_user(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # создание объекта без сохранения в БД
            user.set_password(form.cleaned_data["password"])
            user.save()
            messages.success(
                request,
                f"Registration successful! You can now log in as {user.username}",
            )
            return render(request, "users/register_done.html")
    else:
        form = RegisterUserForm()

    return render(request, "users/register.html", {"form": form})


def create_user(request):
    return HttpResponse("create user")


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse("main_menu"))
