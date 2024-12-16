from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, reverse
from .forms import LoginUserForm, RegisterUserForm, ChangePasswordForm
from .models import Friendship
from django.contrib import messages

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required


def user_home(request):
    return render(request, "users/user_home.html")


@login_required
def user_view_friends(request):
    friends = Friendship.objects.filter(user=request.user).values_list("friend", flat=True)

    context = {"friends": friends}

    return render(request, "users/friends.html", context=context)


def user_add_friend(request):
    return HttpResponse("YES!")


def user_delete_friends(request):
    pass


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
            user = form.save(commit=False)
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


def change_password(request):
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            old_password = form.cleaned_data["password"]
            new_password = form.cleaned_data["password2"]

            user = authenticate(request, username=username, password=old_password)
            if user:
                user.set_password(new_password)
                user.save()

                update_session_auth_hash(request, user)
                messages.success(request, "Your password has been successfully updated!")

                return HttpResponseRedirect(reverse("user_home"))

            else:
                return render(request, "users/change_password.html", {"error": "Wrong password or username", "form": form})
    else:
        form = ChangePasswordForm()

    return render(request, "users/change_password.html", {"form": form})
