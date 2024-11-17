import os

from populate_genres import populate_genres
from populate_movies import populate_movies
from populate_language import populate_language
from populate_metadata import populate_metadata
from populate_movie_languages import populate_movie_languages
from populate_movie_genres import populate_movie_genres
from populate_actors import populate_actors
from populate_movies_actors import populate_movie_actors

if __name__ == "__main__":

    genres = populate_genres()
    movies = populate_movies()
    languages = populate_language()
    metadata = populate_metadata()
    movie_languages = populate_movie_languages()
    movie_genres = populate_movie_genres()
    actors = populate_actors()
    movie_actors = populate_movie_actors()

    # movies.run()
    # metadata.run()
    # genres.run()
    # languages.run()
    actors.run()
    # movie_genres.run()
    # movie_languages.run()
    movie_actors.run()

