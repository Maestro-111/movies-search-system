from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse,HttpResponseNotFound,HttpResponseRedirect
from .models import Movie
from fuzzywuzzy import process
from .models import Movie,MovieMetaData
import numpy as np

# Create your views here.

def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Page not found</h1>')


def enter_query(request):
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

    print(movie)
    print(metadata)

    metadata_values = np.array([value for key, value in metadata.__dict__.items() if key != 'movie_id' and key != '_state'])

    # Step 2: Retrieve all metadata, excluding the one with the given movie_id
    all_metadata = MovieMetaData.objects.exclude(movie_id=movie_id)

    dot_products = []

    for meta in all_metadata:
        if meta.movie_id != movie.movie_id:
            meta_values = np.array([value for key, value in meta.__dict__.items() if key != 'movie_id' and key != '_state'])
            dot_product = np.dot(metadata_values, meta_values)
            dot_products.append([meta.movie_id, dot_product])

    recommended_ids = [movie_id for (movie_id,dot_product) in sorted(dot_products,key=lambda x : x[1],reverse=True)[:10]]

    recommended_movies = Movie.objects.filter(movie_id__in=recommended_ids).values('original_title')

    recommended_movies = []

    for id in recommended_ids:
        try:
            movie_object = Movie.objects.get(movie_id__exact=id)
            recommended_movies.append(movie_object)
        except Exception as e:
            print(e)
            continue

    print(recommended_movies)


    context = {
        'movie':movie,
        'recommendations':recommended_movies
    }

    return render(request,'movie/show_movie.html',context)
