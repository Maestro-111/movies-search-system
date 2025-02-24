from populate_genres import PopulateGenres
from populate_movies import PopulateMovies
from populate_language import PopulateLanguage
from populate_metadata import PopulateMetadata
from populate_movie_languages import PopulateMovieLanguages
from populate_movie_genres import PopulateMovieGenres
from populate_actors import PopulateActors
from populate_movies_actors import PopulateMovieActors

if __name__ == "__main__":
    genres = PopulateGenres()
    movies = PopulateMovies()
    languages = PopulateLanguage()
    metadata = PopulateMetadata()
    movie_languages = PopulateMovieLanguages()
    movie_genres = PopulateMovieGenres()
    actors = PopulateActors()
    movie_actors = PopulateMovieActors()

    movies.run()
    metadata.run()
    genres.run()
    languages.run()
    actors.run()
    movie_genres.run()
    movie_languages.run()
    movie_actors.run()
