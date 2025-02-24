from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseNotFound


def main_menu(request):
    return render(request, "menu/menu.html")


def start_search(request):
    movie_search_url = reverse("search_movie")

    return redirect(movie_search_url)


def user_home(request):
    user_home_url = reverse("users:user_home")
    return redirect(user_home_url)


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1> No such Page!! </h1>")
