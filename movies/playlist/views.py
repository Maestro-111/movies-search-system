import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from movie.models import Movie, MovieMetaData, Rating
from .models import Playlist
from .forms import PlaylistForm, RatingForm

from django.conf import settings
from factorization_machine.recommendations import produce_recommendations
from factorization_machine.recommendations import get_combined_features
from  factorization_machine.precompute_recommendations import group_recommendation

from gensim.models import Word2Vec
from django.db import transaction

from django.core.paginator import Paginator

from django.core.cache import cache


# Create your views here.
# ADD: param to show movie in get_abs_url for movie to pass corresponding url to go back


@login_required
def playlist_menu(request):
    return render(request, "playlist/playlist_menu.html")


@login_required
def create_playlist(request):
    if request.method == "POST":
        play_list_name = request.POST.get("play_list_name")

        existing_playlist = Playlist.objects.filter(name=play_list_name, user=request.user).first()

        if existing_playlist:
            return render(
                request,
                "playlist/create_playlist.html",
                {"error_message": "A playlist with this name already exists."},
            )
        else:
            Playlist.objects.create(name=play_list_name, user=request.user)
            return HttpResponseRedirect(reverse("main_menu"))

    else:
        return render(request, "playlist/create_playlist.html")


@login_required
def view_playlists(request):
    playlists = Playlist.objects.filter(user=request.user)

    context = {"playlists": playlists}
    return render(request, "playlist/view_all_playlists.html", context)


@login_required
def delete_playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id)
    playlist.delete()

    return redirect("view_playlists")


@login_required
def remove_movie_from_playlist(request, playlist_id, movie_id):
    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
    movie = get_object_or_404(Movie, movie_id=movie_id)

    with transaction.atomic():
        playlist.movie.remove(movie)

        rating = Rating.objects.get(movie=movie, user=request.user)
        rating.delete()

    return redirect("view_single_playlist", playlist_id=playlist.id)


@login_required
def view_single_playlist(request, playlist_id: int):
    playlist = get_object_or_404(Playlist, id=playlist_id)
    movies = playlist.movie.all()

    if request.method == "POST" and "name" in request.POST:
        form = PlaylistForm(request.POST, instance=playlist)

        if form.is_valid():
            form.save()
            return redirect("view_single_playlist", playlist_id=playlist.id)
    else:
        form = PlaylistForm(instance=playlist)

    # Handle rating submission
    if request.method == "POST" and "rating" in request.POST:
        movie_id = request.POST.get("movie_id")
        movie = get_object_or_404(Movie, movie_id=movie_id)
        rating_form = RatingForm(request.POST)

        print(movie_id)

        if rating_form.is_valid():
            rating = rating_form.save(commit=False)
            rating.user = request.user
            rating.movie = movie

            print(rating)
            print(rating.rating)
            print(rating.user)
            print(rating.movie)

            existing_rating = Rating.objects.filter(user=request.user, movie=movie).first()

            print(existing_rating)

            if existing_rating:
                existing_rating.rating = rating.rating
                existing_rating.save()
            else:
                try:
                    rating.save()
                except IntegrityError:
                    pass

            return redirect("view_single_playlist", playlist_id=playlist.id)
    else:
        rating_form = RatingForm()

    movie_ratings_display = {movie.movie_id: (rating.rating if rating else None) for movie, rating in zip(movies, [Rating.objects.filter(user=request.user, movie=movie).first() for movie in movies])}

    print(movie_ratings_display)

    context = {
        "movies": movies,
        "playlist": playlist,
        "form": form,
        "rating_form": rating_form,
        "movie_ratings_display": movie_ratings_display,
    }

    return render(request, "playlist/view_single_playlist.html", context)


@login_required
def add_movie_to_playlist(request, movie_id):
    movie = get_object_or_404(Movie, movie_id=movie_id)

    if request.method == "POST":
        play_list_name = request.POST.get("play_list_name")
        playlists = Playlist.objects.filter(user=request.user)

        try:
            playlist = playlists.get(name=play_list_name)
        except Playlist.DoesNotExist:
            error_message = f"The playlist '{play_list_name}' does not exist."
            return render(
                request,
                "playlist/add_movie_to_playlist.html",
                {
                    "movie_id": movie_id,
                    "playlists": playlists,
                    "movie": movie,
                    "error_message": error_message,
                },
            )

        if movie in playlist.movie.all():
            error_message = f"The movie '{movie.original_title}' is already in the playlist '{playlist.name}'."
            playlists = Playlist.objects.filter(user=request.user)

            return render(
                request,
                "playlist/add_movie_to_playlist.html",
                {
                    "movie_id": movie_id,
                    "playlists": playlists,
                    "movie": movie,
                    "error_message": error_message,
                },
            )

        playlist.movie.add(movie)
        return redirect("view_single_playlist", playlist_id=playlist.id)

    playlists = Playlist.objects.filter(user=request.user)

    if not playlists.exists():
        return redirect("create_playlist")

    return render(
        request,
        "playlist/add_movie_to_playlist.html",
        {"movie_id": movie_id, "playlists": playlists, "movie": movie},
    )



@login_required
def get_recommendation_for_playlist(request, playlist_id):

    """
    get recommendations for a user for based on all exact playlist
    """

    cache_key = f"{request.user.id}_{playlist_id}_playlist_recommendations"
    recommendations = cache.get(cache_key)

    if recommendations:

        movie_ids = json.loads(recommendations)
        recommendations = Movie.objects.filter(movie_id__in=movie_ids)

    else:

        wordvec = Word2Vec.load(str(settings.MODEL_DIR))
        playlist = Playlist.objects.get(id=playlist_id)

        selected_movies = set(playlist.movie.all())

        if not selected_movies:
            return render(
                request,
                "playlist/show_recommendations.html",
                {"error_message": "You do not have any movies in your playlists"},
            )

        recommendations = group_recommendation(selected_movies=selected_movies, wordvec=wordvec, user=request.user)

        movie_ids = [movie.movie_id for movie in recommendations]
        cache.set(cache_key, json.dumps(movie_ids), timeout=300)

    paginator = Paginator(recommendations, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"result": page_obj}

    return render(request, "playlist/show_recommendations.html", context=context)


@login_required
def get_my_recommendations(request):

    """
    get recommendations for a user for based on all playlists
    """

    cache_key = f"{request.user.id}_all_recommendations"
    recommendations = cache.get(cache_key)

    if recommendations:

        movie_ids = json.loads(recommendations)
        recommendations = Movie.objects.filter(movie_id__in=movie_ids)

    else:

        wordvec = Word2Vec.load(str(settings.MODEL_DIR))
        playlists = Playlist.objects.filter(user=request.user)

        if not playlists.exists():
            return render(
                request,
                "playlist/show_recommendations.html",
                {"error_message": "You do not have any playlists"},
            )

        selected_movies = set()

        for playlist in playlists:
            selected_movies.update(playlist.movie.all())

        if not selected_movies:
            return render(
                request,
                "playlist/show_recommendations.html",
                {"error_message": "You do not have any movies in your playlists"},
            )

        recommendations = group_recommendation(selected_movies=selected_movies, wordvec=wordvec, user=request.user)

        movie_ids = [movie.movie_id for movie in recommendations]
        cache.set(cache_key, json.dumps(movie_ids), timeout=300)

    paginator = Paginator(recommendations, 10)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"result": page_obj}

    return render(request, "playlist/show_recommendations.html", context=context)
