from django.shortcuts import render
from django.http import HttpResponse,HttpResponseNotFound,HttpResponseRedirect
from .models import Movie
from fuzzywuzzy import process
from .models import Movie,MovieMetaData
import numpy as np

# Create your views here.


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

    metadata = MovieMetaData.objects.filter(movie_id=movie_id)

    all_metadata = MovieMetaData.objects.exclude(movie_id=movie_id)

    metadata_values = [field.name for field in metadata._meta.get_fields() if field.name != 'movie_id']
    print(metadata_values)
    all_metadata_values = [[field.name for field in entry._meta.get_fields() if field.name != 'movie_id'] for entry in all_metadata]
    print(all_metadata_values)

    '''
    dot_products = []
    for movie_id,entry in enumerate(all_metadata_values):
        dot_products.append([movie_id,np.dot(entry,metadata_values)])

    recomendations = [movie_id for movie_id,dot in sorted(dot_products,key=lambda x : x[1])][:10]
    
    print(recomendations)
    '''


    context = {
        'movie':movie
    }

    return render(request,'movie/show_movie.html',context)
