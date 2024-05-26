from django.shortcuts import render
from django.http import HttpResponse,HttpResponseNotFound,HttpResponseRedirect
from .models import Movie
from fuzzywuzzy import process
from .models import Movie

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


    print(movies)

    return render(request, 'movie/search_movie.html', {'movies': movies})



def show_movie(request, movie_id):

    movie = Movie.objects.get(movie_id__exact=movie_id)

    context = {
        'movie':movie
    }

    return render(request,'movie/show_movie.html',context)
