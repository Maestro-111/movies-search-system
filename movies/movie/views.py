from django.shortcuts import render
from .models import Movie, MovieMetaData, Rating, MovieActor

from django.db.models import Q
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector, TrigramSimilarity

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
import os

from config.logger_config import logger

from langdetect import detect
import json

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
        relative_path = "movies/config/languages.json"
        file_path = os.path.join(settings.BASE_DIR, relative_path)

        with open(file_path, "r") as f:
            language_config = json.load(f)

        language = detect(query)
        pg_config = language_config.get(language, "english")  # Fallback to English if language is not found

        # Perform Full Text Search
        search_query = SearchQuery(query, config=pg_config)
        search_vector = SearchVector("original_title", config=pg_config, weight="A")

        # Combine FTS with Trigram Similarity
        movies = (
            Movie.objects.annotate(rank=SearchRank(search_vector, search_query), similarity=TrigramSimilarity("original_title", query))  # Trigram similarity for typo tolerance
            .filter(Q(rank__gte=0.1) | Q(similarity__gte=0.3))  # Filter by either FTS rank or trigram similarity
            .order_by("-rank", "-similarity")
        )  # Sort by rank first, then by similarity

        # Limit results
        movies = list(movies[:10])
        logger.info(f"best mathces for {query} are ': {[movie.original_title for movie in movies]}")

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
            movies = []

            for title in movie_names:
                try:
                    movie_name = re.findall(r"^(.*) \(\d+\)_\d+$", title)
                    year = re.findall(r"\((\d+)\)", title)

                    movie_name = movie_name[0].strip()
                    year = int(year[0])

                    matching_movies = Movie.objects.filter(Q(original_title__icontains=movie_name) & Q(year=year))

                    logger.info(f"ResNet Search results': {[movie.original_title for movie in matching_movies]}")

                    if matching_movies.exists():
                        movies.extend(list(matching_movies))
                    else:
                        logger.info(f"No movies found with the title: {title}")
                except Exception as e:
                    logger.exception(f"Error retrieving movie with title {title}: {e}")

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
    wordvec = Word2Vec.load(str(settings.MODEL_DIR))

    genres = movie.genres.all()
    genres_in_movie = genres.values_list("genre", flat=True)

    languages = movie.languages.all()
    language_in_movie = languages.values_list("language", flat=True)

    movie_actors = MovieActor.objects.filter(movie=movie).select_related("actor")

    if not recommended_ids:
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
