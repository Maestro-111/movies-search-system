import os

from populate_genres import populate_genres
from populate_movies import populate_movies
from populate_language import populate_language
from populate_metadata import populate_metadata
from populate_movie_languages import populate_movie_languages
from populate_movie_genres import populate_movie_genres


if __name__ == "__main__":

    genres = populate_genres()
    movies = populate_movies()
    languages = populate_language()
    metadata = populate_metadata()
    movie_languages = populate_movie_languages()
    movie_genres = populate_movie_genres()

    movies.run()
    metadata.run()
    genres.run()
    languages.run()
    movie_genres.run()
    movie_languages.run()


