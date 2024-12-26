import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movies.settings")
django.setup()

from django.conf import settings

from django.contrib.auth.models import User
from django.utils.crypto import get_random_string


from movie.models import Movie, Rating, MovieMetaData, MovieActor, MovieGenres, MovieLanguages
from playlist.models import Playlist

import random
from django.db import transaction, IntegrityError

import pandas as pd

from pathlib import Path

import random
from django.db import transaction, IntegrityError
from django.db.models import Q

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def create_users(n):
    """
    Create n number of users with random usernames and passwords.

    Args:
        n (int): Number of users to create.

    Returns:
        list: A list of created User objects.
    """

    created_users = []

    for i in range(n):
        username = f"user_{get_random_string(5)}_{i}"
        password = get_random_string(10)

        with open("passwords.txt", "a") as file:
            file.write(f"{username}:{password}\n")

        email = f"{username}@example.com"

        # Create the user
        user = User.objects.create_user(username=username, password=password, email=email)
        created_users.append(user)

    print(f"{n} users created successfully.")

    return created_users


def create_populate_playlists(n_playlists, n_movies, users=None):
    """
    Create n playlists for each user with movies selected based on step-by-step filtering:
    first by genre, then by year, and finally by language.

    Args:
        n_playlists (int): Number of playlists to create for each user.
        n_movies (int): Number of movies to add to each playlist.
        users (QuerySet or list, optional): A list or queryset of users. If None, fetch all users.
    """

    if users is None:
        users = User.objects.all()  # Fetch all users if not provided

    movies = Movie.objects.all()

    if not movies.exists():
        print("No movies found in the database. Add some movies first.")
        return

    genres = MovieGenres.objects.all()
    years = movies.values_list("year", flat=True).distinct()
    languages = MovieLanguages.objects.all()

    for user in users:

        for i in range(n_playlists):

            playlist_name = f"Playlist_{user.username}_{i + 1}"

            random_genre = random.choice(genres) if genres.exists() else None
            if random_genre:
                genre_filtered_movies = movies.filter(genres=random_genre)
            else:
                genre_filtered_movies = movies

            # Step 2: Filter by random year from the genre-filtered movies
            available_years = genre_filtered_movies.values_list("year", flat=True).distinct()
            random_year = random.choice(available_years) if available_years else None

            if random_year:
                year_filtered_movies = genre_filtered_movies.filter(year=random_year)
            else:
                year_filtered_movies = genre_filtered_movies

            # Step 3: Filter by random language from the year-filtered movies
            available_languages = year_filtered_movies.values_list("languages__language", flat=True).distinct()
            available_languages = [language for language in available_languages if language]

            language_weights = {lang: 9 if lang.lower() == "english" else 1 for lang in available_languages}

            random_language = random.choices(
                population=list(language_weights.keys()),
                weights=list(language_weights.values()),
                k=1
            )[0] if available_languages else None

            if random_language:
                final_filtered_movies = year_filtered_movies.filter(languages__language=random_language)
            else:
                final_filtered_movies = year_filtered_movies

            # Add up to n_movies from the final filtered movies
            if final_filtered_movies.exists():
                random_movies = random.sample(list(final_filtered_movies), min(len(final_filtered_movies), n_movies))

                try:
                    with transaction.atomic():
                        playlist = Playlist.objects.create(name=playlist_name, user=user)
                        playlist.movie.set(random_movies)
                except IntegrityError as e:
                    print(f"Failed to create playlist for user {user.username}: {e}")
            else:
                print(f"No movies found with the selected filters for user {user.username}.")

        print(f"Created {n_playlists} playlists for user: {user.username}")



def assign_ratings_via_playlists(min_rating=1, max_rating=5):
    """
    Assign random ratings to movies for each user based on their playlists.

    Args:
        min_rating (int): Minimum rating value (inclusive).
        max_rating (int): Maximum rating value (inclusive).
    """

    users = User.objects.filter(username__startswith="user_")  # Only target created users

    if not users.exists():
        print("No users found to assign ratings.")
        return

    with transaction.atomic():
        for user in users:
            playlists = Playlist.objects.filter(user=user)
            movies = set(movie for playlist in playlists for movie in playlist.movie.all())

            if not movies:
                print(f"No movies found in playlists for user: {user.username}")
                continue

            for movie in movies:
                rating_value = random.randint(min_rating, max_rating)  # Random rating

                Rating.objects.update_or_create(user=user, movie=movie, defaults={"rating": rating_value})

            print(f"Assigned ratings for {len(movies)} movies to user: {user.username}")

    print("Ratings assigned to movies via playlists successfully.")


def output_data(output_file="ratings_data.xlsx"):
    """
    Outputs all data from the Rating model combined with movie metadata into an Excel file.

    Args:
        output_file (str): Name of the output Excel file. Defaults to "ratings_data.xlsx".

    Returns:
        None
    """

    ratings = Rating.objects.select_related("user", "movie").all()
    movie_metadata = {meta.movie_id: meta for meta in MovieMetaData.objects.all()}

    if not ratings.exists():
        print("No ratings data found.")
        return

    data = []

    for rating in ratings:

        metadata = movie_metadata.get(rating.movie.movie_id)
        movie = rating.movie

        if metadata:
            meta_features = [getattr(metadata, feature, None) for feature in settings.FEATURES]
        else:
            meta_features = [None] * len(settings.FEATURES)

        movie_actors = MovieActor.objects.filter(movie=movie).select_related("actor")

        actors = ", ".join([movie_actor.actor.actor_name or "Unknown Actor" for movie_actor in movie_actors])
        charaters = ", ".join([movie_actor.character_name or "Unknown Character" for movie_actor in movie_actors])

        text = (
            f"{movie.original_title}, a {', '.join([genre.genre for genre in movie.genres.all()])} movie "
            f"in {', '.join([language.language for language in movie.languages.all()])} from {movie.year or 'an unknown year'}. "
            f"Actors: {actors}. "
            f"Characters: {charaters}. "
            f"{movie.overview or ''}"
        )

        row = {
            "User": rating.user.username,
            "Movie": text,
            "Rating": rating.rating,
        }



        # row.update({feature: value for feature, value in zip(settings.FEATURES, meta_features)})
        data.append(row)

    df = pd.DataFrame(data)
    df.to_excel(output_file, index=False)

    print(f"Ratings data successfully written to {output_file}.")


def remove_random_data():
    """
    Removes data added by the random data creation functions:
    - Removes all ratings for movies and users.
    - Clears all movies from playlists.
    - Deletes all playlists created by the function.
    - Deletes users with usernames matching the pattern used for creation.
    """

    with transaction.atomic():
        # Step 1: Remove all ratings for movies rated by the created users
        users = User.objects.filter(username__startswith="user_")  # Target created users
        ratings = Rating.objects.filter(user__in=users)  # Ratings by these users
        deleted_ratings_count, _ = ratings.delete()
        print(f"Deleted {deleted_ratings_count} ratings.")

        # Step 2: Remove all movies from playlists
        playlists = Playlist.objects.filter(name__startswith="Playlist_")
        for playlist in playlists:
            playlist.movie.clear()  # Clear the many-to-many relationship

        print(f"Cleared movies from {playlists.count()} playlists.")

        # Step 3: Delete all playlists created by the function
        deleted_playlists_count, _ = playlists.delete()
        print(f"Deleted {deleted_playlists_count} playlists.")

        # Step 4: Delete users created by the function
        deleted_users_count, _ = users.delete()
        print(f"Deleted {deleted_users_count} users.")

        # Step 5: Clear the passwords file
        with open("passwords.txt", "w") as file:
            file.write("")

        print("Cleared passwords file.")

        print("Random data cleanup complete.")


if __name__ == "__main__":
    #
    # create_users(70)
    # create_populate_playlists(20, 15)
    # assign_ratings_via_playlists()
    #
    # remove_random_data()
    output_data(output_file=os.path.join(BASE_DIR, "movies/data/ratings_data.xlsx"))
