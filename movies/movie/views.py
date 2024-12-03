from django.shortcuts import render
from fuzzywuzzy import process
from .models import Movie, MovieMetaData, Rating, MovieActor

from django.db.models import Q

from django.core.cache import cache
from sentence_transformers import SentenceTransformer

from recommendations import produce_recommendations
from recommendations import get_combined_features

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from gensim.models import Word2Vec
from chroma_db import chroma_client

import torch
from generate_image_embeddings import get_model_pipeline
from PIL import Image, UnidentifiedImageError

import warnings
import re

from config.logger_config import logger

# Ignore all warnings
warnings.filterwarnings("ignore")
model = SentenceTransformer("all-MiniLM-L6-v2")

@csrf_exempt
def chat_bot_request(request):
    if request.method == "POST":
        user_message = request.POST.get("chat_bot_request", "")
        user_embedding = model.encode(user_message).tolist()

        movies_collection = chroma_client.get_collection("movies_embeddings")

        results = movies_collection.query(
            query_embeddings=[user_embedding],
            n_results=10,
        )

        movie_ids = results["ids"][0]
        movies = [Movie.objects.get(movie_id=cur_id) for cur_id in movie_ids]

        print(movie_ids)
        print(movies)

        return render(request, "movie/search_movie.html", {"movies": movies})

    return render(request, "movie/search_movie.html")


def enter_query(request):
    """
    display search menu
    """

    return render(request, "movie/search_movie.html")


def movie_search(request):
    """
    Find the best matches for the query using fuzzy matching or image embeddings.
    """

    query = request.POST.get("query")
    image = request.FILES.get("image")  # Check if an image was uploaded

    movies = None

    if query:

        all_movies = Movie.objects.all()
        movie_titles = [movie.original_title for movie in all_movies]

        # Get best matches using fuzzywuzzy
        best_matches = process.extract(query, movie_titles, limit=20)
        best_match_titles = [match[0] for match in best_matches if match[1] >= 90]
        title_to_score = {match[0]: match[1] for match in best_matches}

        movies = list(Movie.objects.filter(original_title__in=best_match_titles))

        logger.info(f"Displaying best matches {best_match_titles}: for {query}")

        for movie in movies:
            movie.score = title_to_score.get(movie.original_title, 0)

        # Sort movies by score
        movies.sort(key=lambda x: x.score, reverse=True)

    if image:
        posters_collection = chroma_client.get_collection("posters_collection")
        resnet, transform = get_model_pipeline()

        try:
            img = Image.open(image).convert("RGB")  # Ensure RGB format
            image_tensor = transform(img).unsqueeze(0)

            with torch.no_grad():
                embedding = resnet(image_tensor)

            embedding = embedding.squeeze().numpy()

            # Query ChromaDB for similar posters
            results = posters_collection.query(
                query_embeddings=[embedding],
                n_results=10,
            )

            movie_names = results["ids"][0]

            print(movie_names)

            movies = []

            for title in movie_names:
                movie_name = re.findall(r"^(.*) \(\d+\)_\d+$", title)
                year = re.findall(r"\((\d+)\)", title)

                print(movie_name)
                print(year)

                try:
                    movie_name = re.findall(r"^(.*) \(\d+\)_\d+$", title)
                    year = re.findall(r"\((\d+)\)", title)

                    movie_name = movie_name[0].strip()
                    year = int(year[0])

                    matching_movies = Movie.objects.filter(Q(original_title__icontains=movie_name) & Q(year=year))

                    if matching_movies.exists():
                        movies.extend(list(matching_movies))
                    else:
                        print(f"No movies found with the title: {title}")
                except Exception as e:
                    print(f"Error retrieving movie with title {title}: {e}")

        except UnidentifiedImageError:
            return render(request, "movie/search_movie.html", {"error": "Invalid image format"})
        except Exception as e:
            return render(
                request,
                "movie/search_movie.html",
                {"error": f"Error processing image: {e}"},
            )

    return render(request, "movie/search_movie.html", {"movies": movies})


def show_movie(request, movie_id):
    """
    show selected movie and display recommendations
    """

    cache_key = f"recommended_ids_{movie_id}"
    recommended_ids = cache.get(cache_key)

    movie = Movie.objects.get(movie_id__exact=movie_id)
    metadata = MovieMetaData.objects.get(movie_id=movie_id)

    wordvec = Word2Vec.load(str(settings.MODEL_DIR))

    genres = movie.genres.all()
    genres_in_movie = genres.values_list("genre", flat=True)

    languages = movie.languages.all()
    language_in_movie = languages.values_list("language", flat=True)

    movie_actors = MovieActor.objects.filter(movie=movie).select_related("actor")

    actors = [movie_actor.actor.actor_name for movie_actor in movie_actors]
    characters = [movie_actor.character_name for movie_actor in movie_actors]

    print("!")
    print(movie_actors)
    print(actors)
    print(characters)
    print("!")

    if not recommended_ids:
        print(movie)
        print(metadata)
        print(genres_in_movie)
        print(language_in_movie)

        all_metadata = list(MovieMetaData.objects.all().select_related("movie"))
        all_metadata_dict = {meta.movie_id: meta for meta in all_metadata}

        if request.user.is_authenticated:
            user_ratings = {rating.movie.movie_id: rating.rating for rating in Rating.objects.filter(user=request.user)}
        else:
            user_ratings = {}

        cur_row_metadata_values = get_combined_features(all_metadata_dict.get(movie.movie_id), movie.overview, wordvec)

        metadata_rows = [
            (
                meta.movie_id,
                get_combined_features(meta, all_metadata_dict[meta.movie_id].movie.overview, wordvec),
            )
            for meta in all_metadata
            if meta.movie_id != movie.movie_id
        ]

        recommended_ids = produce_recommendations(cur_row_metadata_values, metadata_rows, user_ratings)
        cache.set(cache_key, recommended_ids, timeout=300)

    recommended_movies = []

    for id in recommended_ids:
        try:
            recommended_movies.append(Movie.objects.get(movie_id__exact=id))
        except Exception as e:
            print(e)
            continue

    context = {
        "movie": movie,
        "produce_recommendations": recommended_movies,
        "spoken_languages": language_in_movie,
        "genres": genres_in_movie,
        "movie_actors": movie_actors,
    }

    return render(request, "movie/show_movie.html", context)
