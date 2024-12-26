from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, reverse, get_object_or_404, redirect
from .forms import LoginUserForm, RegisterUserForm, ChangePasswordForm
from .models import Friendship, Profile
from django.contrib import messages

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.db.models import Q


def create_user_info(username):

    context = {}

    user = User.objects.get(username=username)
    is_friend = Friendship.objects.filter(user=user).exists()

    context['user_name'] = username
    context['user_email'] = user.email
    context['user_date_joined'] = user.date_joined.strftime("%B %d, %Y")
    context['user_is_friend'] = is_friend
    context['user_id'] = user.id

    return context



def user_home(request):
    return render(request, "users/user_home.html")


@login_required
def user_add_friends(request, friend_id):

    user = request.user

    friend = get_object_or_404(User, id=friend_id)
    context = create_user_info(friend.username)


    if user == friend:
        context = {**context, **{"message": "You cannot add yourself as a friend.", "message_type": "error"}}

        return render(
            request,
            "users/show_friend.html",
            context = context,
        )

    if Friendship.objects.filter(user=user, friend=friend).exists() or Friendship.objects.filter(user=friend, friend=user).exists():

        context = {**context, **{"message": "You are already friends with this user.", "message_type": "error"}}

        return render(
            request,
            "users/show_friend.html",
            context = context,
        )

    Friendship.objects.create(user=user, friend=friend)
    Friendship.objects.create(user=friend, friend=user)

    context = {**context, **{"message":  f"You are now friends with {friend.username}!", "message_type": "success"}}

    return render(
        request,
        "users/show_friend.html",
        context = context,
    )


def show_user(request, username):

    context = create_user_info(username)

    return render(request, "users/show_friend.html", context=context)



@login_required
def user_view_friends(request):

    friend_ids = Friendship.objects.filter(user=request.user).values_list("friend", flat=True)
    friends = User.objects.filter(id__in=friend_ids)

    users_with_profiles = friends.select_related("profile")

    paginator = Paginator(users_with_profiles, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"friends": page_obj}
    return render(request, "users/friends.html", context=context)


def user_search(request):

    query = request.POST.get("query")
    users_with_profiles = {}

    if query:

        users = User.objects.filter(Q(username__icontains=query) |
                                    Q(email__icontains=query) |
                                    Q(first_name__icontains=query) |
                                    Q(last_name__icontains=query) |
                                    Q(first_name__icontains=query.split()[0],
                                    last_name__icontains=query.split()[-1]))[:10]

        users_with_profiles = users.select_related("profile")

    return render(request, "users/user_search.html", {"users": users_with_profiles})


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
