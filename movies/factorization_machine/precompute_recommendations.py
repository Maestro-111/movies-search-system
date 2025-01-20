from django.conf import settings
import os

import json

from movie.models import Movie, MovieMetaData, Rating
from playlist.models import Playlist

from django.conf import settings

from factorization_machine.recommendations import produce_recommendations
from factorization_machine.recommendations import get_combined_features
from django.contrib.auth.models import User

from gensim.models import Word2Vec

from django.core.cache import cache



def user_playlist_recommendations():

    users = User.objects.all()
    wordvec = Word2Vec.load(str(settings.MODEL_DIR))

    for user in users:

        print(user.username)

        playlists = Playlist.objects.filter(user=user)

        for playlist in playlists:

            selected_movies = set(playlist.movie.all())

            recommendations = group_recommendation(selected_movies, wordvec, user=user)

            movie_ids = [movie.movie_id for movie in recommendations]

            cache_key = f"{user.id}_{playlist.id}_playlist_recommendations"
            cache.set(cache_key, json.dumps(movie_ids), timeout=86400)  # Cache for 24 hours

        break


def user_all_recommendations():


    """
    first we call user_playlist_recommendations, then just combine results of that by cache and store

    cache = user.id_all_recommendations

    """

    pass



def group_recommendation(selected_movies, wordvec, user):

    """
    gather data for recommendation computation
    """

    seen_titles = {movie.original_title for movie in selected_movies}
    recommendations = set()

    meta_data_names = [field for field in settings.FEATURES]


    all_metadata = list(MovieMetaData.objects.all().select_related("movie"))
    all_metadata_dict = {meta.movie_id: meta for meta in all_metadata}

    user_ratings = {rating.movie.movie_id: rating.rating for rating in Rating.objects.filter(user=user)}

    for movie in selected_movies:
        cur_metadata = all_metadata_dict.get(movie.movie_id)

        if not cur_metadata:
            continue

        cur_row_metadata_values = get_combined_features(cur_metadata, movie.overview, wordvec)

        metadata_rows = [
            (
                meta.movie_id,
                get_combined_features(meta, all_metadata_dict[meta.movie_id].movie.overview, wordvec),
            )
            for meta in all_metadata
            if meta.movie_id != movie.movie_id
        ]

        recommended_movie_ids = produce_recommendations(cur_row_metadata_values, metadata_rows, user_ratings, metadata_name=meta_data_names, user=user)
        recommended_movies = [Movie.objects.get(movie_id=id) for id in recommended_movie_ids if id in all_metadata_dict and all_metadata_dict[id].movie.original_title not in seen_titles]

        recommendations.update(recommended_movies[:3])

    return list(recommendations)


if __name__ == '__main__':
    user_playlist_recommendations()