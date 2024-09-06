from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse,HttpResponseNotFound,HttpResponseRedirect
from .models import Movie
from fuzzywuzzy import process
from .models import Movie,MovieMetaData,Rating
import numpy as np
from numba import jit

from django.core.cache import cache

from recommendations import produce_recommendations
from recommendations import get_text_vectors
from recommendations import get_combined_features

from django.conf import settings

from gensim.models import Word2Vec

import joblib

import warnings

# Ignore all warnings
warnings.filterwarnings('ignore')

# Create your views here.


def enter_query(request):

    """
    display search menu
    """

    return render(request,'movie/search_movie.html')


def movie_search(request):

    query = request.GET.get('query')
    movies = None

    if query:
        all_movies = Movie.objects.all()
        movie_titles = [movie.original_title for movie in all_movies]

        best_matches = process.extract(query, movie_titles, limit=5)

        best_match_titles = [match[0] for match in best_matches if match[1] >= 90]  # Adjust threshold as needed

        best_match_titles = [match[0] for match in best_matches]
        title_to_score = {match[0]: match[1] for match in best_matches}

        movies = list(Movie.objects.filter(original_title__in=best_match_titles))
        for movie in movies:
            movie.score = title_to_score[movie.original_title]

        # Sort movies by score
        movies.sort(key=lambda x: x.score, reverse=True)


    #print(movies)

    return render(request, 'movie/search_movie.html', {'movies': movies})


def show_movie(request, movie_id):

    cache_key = f"recommended_ids_{movie_id}"
    recommended_ids = cache.get(cache_key)

    movie = Movie.objects.get(movie_id__exact=movie_id)
    metadata = MovieMetaData.objects.get(movie_id=movie_id)

    wordvec = Word2Vec.load(str(settings.MODEL_DIR))

    genres = movie.genres.all()
    genres_in_movie = genres.values_list('genre', flat=True)

    languages = movie.languages.all()
    language_in_movie = languages.values_list('language', flat=True)

    if not recommended_ids:

        print(movie)
        print(metadata)
        print(genres_in_movie)
        print(language_in_movie)

        all_metadata = list(MovieMetaData.objects.all().select_related('movie'))
        all_metadata_dict = {meta.movie_id: meta for meta in all_metadata}

        if request.user.is_authenticated:
            user_ratings = {rating.movie.movie_id: rating.rating for rating in Rating.objects.filter(user=request.user)}
        else:
            user_ratings = {}

        cur_row_metadata_values = get_combined_features(all_metadata_dict.get(movie.movie_id), movie.overview, wordvec)

        metadata_rows = [
            (meta.movie_id, get_combined_features(meta, all_metadata_dict[meta.movie_id].movie.overview, wordvec))
            for meta in all_metadata if meta.movie_id != movie.movie_id
        ]

        recommended_ids = produce_recommendations(cur_row_metadata_values, metadata_rows, user_ratings)
        cache.set(cache_key, recommended_ids, timeout=300)

    recommended_movies = []

    for id in recommended_ids:
        try:
            recommended_movies.append(Movie.objects.get(movie_id__exact=id))
        except Exception as e:
            print(e)
            continue

    context = {
        'movie':movie,
        'produce_recommendations':recommended_movies,
        'spoken_languages':language_in_movie,
        'genres':genres_in_movie
    }

    return render(request,'movie/show_movie.html',context)
