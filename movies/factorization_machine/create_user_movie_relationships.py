import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movies.settings")
django.setup()


from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

from django.conf import settings

from movie.models import Movie,Rating,MovieMetaData
from playlist.models import Playlist

import random
from django.db import transaction, IntegrityError

import pandas as pd
import numpy as np

from pathlib import Path
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
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )
        created_users.append(user)

    print(f"{n} users created successfully.")

    return created_users


def create_populate_playlists(n_playlists, n_movies, users=None):

    """
       Create n playlists for each user with random movies.

       Args:
           n (int): Number of playlists to create for each user.
           users (QuerySet or list, optional): A list or queryset of users. If None, fetch all users.


       """

    if users is None:
        users = User.objects.all()  # Fetch all users if not provided

    movies = list(Movie.objects.all())  # Fetch all movies

    if not movies:
        print("No movies found in the database. Add some movies first.")
        return

    for user in users:

        for i in range(n_playlists):

            playlist_name = f"Playlist_{user.username}_{i + 1}"
            random_movies = random.sample(movies, min(n_movies, len(movies)))

            try:
                with transaction.atomic():
                    playlist = Playlist.objects.create(name=playlist_name, user=user)
                    playlist.movie.set(random_movies)
            except IntegrityError as e:
                print(f"Failed to create playlist for user {user.username}: {e}")


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

                Rating.objects.update_or_create(
                    user=user,
                    movie=movie,
                    defaults={"rating": rating_value}
                )

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

    # Collect data for the DataFrame
    data = []

    for rating in ratings:
        metadata = movie_metadata.get(rating.movie.movie_id)  # Ensure correct key access

        # Extract metadata features
        if metadata:
            meta_features = [getattr(metadata, feature, None) for feature in settings.FEATURES]
        else:
            meta_features = [None] * len(settings.FEATURES)

        # Add rating data and metadata to the row
        row = {
            "User": rating.user.username,
            "Movie": rating.movie.original_title,
            "Rating": rating.rating,
        }
        row.update({feature: value for feature, value in zip(settings.FEATURES, meta_features)})

        data.append(row)

    # Create a DataFrame from the collected data
    df = pd.DataFrame(data)

    # Export to Excel
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

    create_users(n=100)
    create_populate_playlists(n_playlists=50, n_movies=10, users=None)

    assign_ratings_via_playlists()
    output_data(output_file=os.path.join(BASE_DIR, "movies/data/ratings_data.xlsx"))

    # remove_random_data()