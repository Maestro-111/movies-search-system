from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse,HttpResponseNotFound,HttpResponseRedirect
from .models import Movie
from fuzzywuzzy import process
from .models import Movie,MovieMetaData
import numpy as np
from numba import jit

from recommendations import produce_recommendations
from recommendations import get_text_vectors

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

    movie = Movie.objects.get(movie_id__exact=movie_id)
    metadata = MovieMetaData.objects.get(movie_id=movie_id)

    model = Word2Vec.load(settings.MODEL_DIR)
    pca = joblib.load(settings.PCA_DIR)

    genres = movie.genres.all()
    genres_in_movie = genres.values_list('genre', flat=True)

    languages = movie.languages.all()
    language_in_movie = languages.values_list('language', flat=True)

    text_features = get_text_vectors(movie.overview,model)

    print(movie)
    print(text_features)
    print(metadata)
    print(genres_in_movie)
    print(language_in_movie)

    cur_row_metadata_values = np.array([value for key, value in metadata.__dict__.items() if key in set(settings.FEATURES)])
    cur_row_metadata_values = pca.transform(cur_row_metadata_values.reshape(1, -1)).reshape(-1)

    cur_row_metadata_values = np.concatenate([cur_row_metadata_values, text_features])
    all_metadata = MovieMetaData.objects.exclude(movie_id=movie_id)

    metadata_rows = []

    for meta in all_metadata:
        if meta.movie_id != movie.movie_id:

            meta_movie = Movie.objects.get(movie_id__exact=meta.movie_id)
            text_features = get_text_vectors(meta_movie.overview, model)

            meta_values = np.array([value for key, value in meta.__dict__.items() if key in set(settings.FEATURES)])
            meta_values = pca.transform(meta_values.reshape(1, -1)).reshape(-1)

            meta_values = np.concatenate([meta_values,text_features])
            metadata_rows.append([meta.movie_id,meta_values])

    recommended_ids = produce_recommendations(cur_row_metadata_values, metadata_rows)
    recommended_movies = []

    for id in recommended_ids:
        try:
            movie_object = Movie.objects.get(movie_id__exact=id)
            recommended_movies.append(movie_object)
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
