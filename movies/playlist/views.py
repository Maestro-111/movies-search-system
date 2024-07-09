from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse,HttpResponseNotFound,HttpResponseRedirect

from movie.models import Movie, MovieMetaData
from .models import Playlist

import numpy as np

from django.conf import settings

from recommendations import produce_recommendations
from recommendations import get_text_vectors

from gensim.models import Word2Vec

import random

# Create your views here.


# ADD: param to show movie in get_abs_url for movie to pass corresponding url to go back


@login_required
def playlist_menu(request):

    return render(request, 'playlist/playlist_menu.html')

@login_required
def create_playlist(request):

    if request.method == 'POST':
        play_list_name = request.POST.get('play_list_name')

        existing_playlist = Playlist.objects.filter(name=play_list_name, user=request.user).first()

        if existing_playlist:
            return render(request, 'playlist/create_playlist.html',
                          {
                              'error_message': 'A playlist with this name already exists.'
                          }
                          )
        else:
            Playlist.objects.create(name=play_list_name, user=request.user)

            movie_id = request.GET.get('movie_id')

            # if movie_id:
            #     return redirect('add_movie_to_playlist', movie_id=movie_id)

            return HttpResponseRedirect(reverse('main_menu'))

    else:
        return render(request, 'playlist/create_playlist.html')


@login_required
def view_playlists(request):

    playlists = Playlist.objects.filter(user=request.user)



    context = {
        "playlists":playlists
    }

    return render(request, 'playlist/view_all_playlists.html',context)

@login_required
def delete_playlist(request, playlist_id):

    playlist = get_object_or_404(Playlist, id=playlist_id)
    playlist.delete()

    return redirect('view_playlists')


@login_required
def remove_movie_from_playlist(request, playlist_id, movie_id):

    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
    movie = get_object_or_404(Movie, movie_id=movie_id)

    playlist.movie.remove(movie)

    return redirect('view_single_playlist', playlist_id=playlist.id)

@login_required
def view_single_playlist(request, playlist_id:int):



    playlist = get_object_or_404(Playlist, id=playlist_id)
    movies = playlist.movie.all()

    context = {
        "movies":movies,
        "playlist":playlist
    }

    return render(request, 'playlist/view_single_playlist.html',context)



@login_required
def add_movie_to_playlist(request, movie_id):

    movie = get_object_or_404(Movie, movie_id=movie_id)

    if request.method == 'POST':

        play_list_name = request.POST.get('play_list_name')
        playlists = Playlist.objects.filter(user=request.user)

        try:
            playlist = playlists.get(name=play_list_name)
        except Playlist.DoesNotExist:
            error_message = f"The playlist '{play_list_name}' does not exist."
            return render(request, 'playlist/add_movie_to_playlist.html', {
                'movie_id': movie_id,
                'playlists': playlists,
                'movie': movie,
                'error_message': error_message
            })

        if movie in playlist.movie.all():

            error_message = f"The movie '{movie.original_title}' is already in the playlist '{playlist.name}'."
            playlists = Playlist.objects.filter(user=request.user)

            return render(request, 'playlist/add_movie_to_playlist.html', {
                'movie_id': movie_id,
                'playlists': playlists,
                'movie': movie,
                'error_message': error_message
            })

        playlist.movie.add(movie)
        return redirect('view_single_playlist', playlist_id=playlist.id)

    playlists = Playlist.objects.filter(user=request.user)

    if not playlists.exists():
        return redirect('create_playlist')

    return render(request, 'playlist/add_movie_to_playlist.html', {'movie_id': movie_id,
                                                                   'playlists': playlists,
                                                                   'movie':movie})



@login_required
def get_my_recommendations(request):

    model = Word2Vec.load(settings.MODEL_DIR)
    playlists = Playlist.objects.filter(user=request.user)

    if not playlists.exists():
        return render(request, 'playlist/show_recommendations.html', {"error_message":"You do not have any playlists"})


    selected_movies = []
    seen = set()

    for playlist in playlists:

        movies = playlist.movie.all()

        if movies:
            for movie in movies:
                selected_movies.append(movie)
                seen.add(movie.original_title)

    if not selected_movies:
        return render(request, 'playlist/show_recommendations.html', {"error_message": "You do not have any movies"
                                                                                       " in you playlists"})

    print(selected_movies)

    result = set()

    for movie in selected_movies:

        metadata = MovieMetaData.objects.get(movie_id=movie.movie_id)
        text_features = get_text_vectors(movie.overview, model)

        cur_row_metadata_values = np.array(
            [value for key, value in metadata.__dict__.items() if key in set(settings.FEATURES)])
        cur_row_metadata_values = np.concatenate([cur_row_metadata_values, text_features])

        all_metadata = MovieMetaData.objects.exclude(movie_id=movie.movie_id)

        metadata_rows = []

        for meta in all_metadata:

            if meta.movie_id != movie.movie_id:

                meta_movie = Movie.objects.get(movie_id__exact=meta.movie_id)
                text_features = get_text_vectors(meta_movie.overview, model)

                meta_values = np.array(
                    [value for key, value in meta.__dict__.items() if key in set(settings.FEATURES)])
                meta_values = np.concatenate([meta_values, text_features])

                metadata_rows.append([meta.movie_id, meta_values])

        recommended_movies = [Movie.objects.get(movie_id__exact=id) for id in produce_recommendations(cur_row_metadata_values, metadata_rows)]
        recommended_movies = [movie for movie in recommended_movies if movie.original_title not in seen]

        k = random.randint(1, len(recommended_movies))
        sample = random.sample(recommended_movies, k=k)

        for movie in sample:
            if movie not in result:
                result.add(movie)

    result = list(result)

    return render(request, 'playlist/show_recommendations.html', {'result':result})




