from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from movie.models import Movie, MovieMetaData, Rating
from .models import Playlist
from .forms import PlaylistForm, RatingForm

from django.conf import settings
from recommendations import produce_recommendations
from recommendations import get_combined_features

from gensim.models import Word2Vec
from django.db import transaction
import random


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


def group_recommendation(request, selected_movies, wordvec):

    seen_titles = {movie.original_title for movie in selected_movies}
    recommendations = set()

    all_metadata = list(MovieMetaData.objects.all().select_related("movie"))
    all_metadata_dict = {meta.movie_id: meta for meta in all_metadata}

    user_ratings = {rating.movie.movie_id: rating.rating for rating in Rating.objects.filter(user=request.user)}

    for movie in selected_movies:
        cur_metadata = all_metadata_dict.get(movie.movie_id)

        if not cur_metadata:
            continue

        cur_row_metadata_values = get_combined_features(cur_metadata, movie.overview, wordvec)

        metadata_rows = [
            (
                meta.movie_id,
                get_combined_features(meta, all_metadata_dict[meta.movie_id].movie.overview, wordvec),
            )
            for meta in all_metadata
            if meta.movie_id != movie.movie_id
        ]

        recommended_movie_ids = produce_recommendations(cur_row_metadata_values, metadata_rows, user_ratings)

        """
        Rank?
        """

        recommended_movies = [Movie.objects.get(movie_id=id) for id in recommended_movie_ids if id in all_metadata_dict and all_metadata_dict[id].movie.original_title not in seen_titles]

        sample_size = min(random.randint(1, len(recommended_movies)), 10)
        recommendations.update(random.sample(recommended_movies, k=sample_size))

    return list(recommendations)


@login_required
def get_recommendation_for_playlist(request, playlist_id):
    """
    get recommendations for a user for based on all exact playlist
    """

    wordvec = Word2Vec.load(str(settings.MODEL_DIR))
    playlist = Playlist.objects.get(id=playlist_id)

    selected_movies = set(playlist.movie.all())

    if not selected_movies:
        return render(
            request,
            "playlist/show_recommendations.html",
            {"error_message": "You do not have any movies in your playlists"},
        )

    recommendations = group_recommendation(request, selected_movies=selected_movies, wordvec=wordvec)
    return render(request, "playlist/show_recommendations.html", {"result": recommendations})


@login_required
def get_my_recommendations(request):
    """
    get recommendations for a user for based on all playlists
    """

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

    recommendations = group_recommendation(request, selected_movies=selected_movies, wordvec=wordvec)
    return render(request, "playlist/show_recommendations.html", {"result": recommendations})
