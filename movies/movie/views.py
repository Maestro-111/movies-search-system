from django.shortcuts import render
from .models import Movie, MovieMetaData, Rating, MovieActor, MovieGenres

from django.db.models import Q
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector, TrigramSimilarity

from django.core.cache import cache
from sentence_transformers import SentenceTransformer

from factorization_machine.recommendations import produce_recommendations
from factorization_machine.recommendations import get_combined_features

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from gensim.models import Word2Vec

from django.core.paginator import Paginator

from embeddings.chroma_db import chroma_client

import torch
from embeddings.model_pipeline import get_model_pipeline
from PIL import Image, UnidentifiedImageError

import warnings
import re
import os

from config.logger_config import system_logger

from langdetect import detect
import json

from collections import defaultdict

# import spacy
# from embeddings.train_spacy import MODEL_PATH


# Ignore all warnings
warnings.filterwarnings("ignore")
model = SentenceTransformer("all-MiniLM-L6-v2")

# try:
#     nlp = spacy.load(MODEL_PATH)
#     print("Loaded trained movie model successfully!")
# except Exception as e:
#     print(e)
#     print("Couldn't load trained model - please run training script first")
#     nlp = None

nlp = None


# def extract_query_filters(query: str):
#     try:
#         nlp = spacy.load("embeddings/trained_movie_model")
#         print("Loaded trained movie model successfully!")
#     except:
#         print("Couldn't load trained model - please run training script first")
#         nlp = None
#
#     filters = defaultdict(list)
#
#     year_match = re.search(r'\b(19|20)\d{2}\b', query)
#
#     if year_match:
#         filters['year'] = [int(year_match.group())]
#
#     actor_names = set(MovieActor.objects.values_list('actor__actor_name', flat=True).distinct())
#
#     for actor_name in actor_names:
#         if actor_name and actor_name.lower() in query.lower():
#             filters['actor'].append(actor_name)
#
#     genres = set(MovieGenres.objects.values_list('genre', flat=True))
#
#     for genre in genres:
#         if genre.lower() in query.lower():
#             filters['genre'].append(genre)
#
#     return filters

def extract_query_filters(query: str):

    if nlp is None:
        return defaultdict(list)

    doc = nlp(query)
    filters = defaultdict(list)

    for ent in doc.ents:
        if ent.label_ == "DATE":
            try:
                year = int(ent.text)
                if year < 100:
                    year += 2000 if year < 50 else 1900
                filters['year'].append(year)
            except ValueError:
                pass
        elif ent.label_ == "GENRE":
            filters['genre'].append(ent.text)
        elif ent.label_ == "ACTOR":
            filters['actor'].append(ent.text)

    print(filters)
    return filters


@csrf_exempt
def chat_bot_request(request):

    """
    ask a chatbot. Users test is a text in a natural language.
    we use embeddings in chroma db to get closest 10
    """

    if request.method == "POST":

        user_message = request.POST.get("chat_bot_request", "")

        filters = extract_query_filters(user_message)

        queryset = Movie.objects.all()

        if 'year' in filters:

            year_q = Q()

            for year in filters['year']:
                year_q |= Q(year=year)

            queryset = queryset.filter(year_q)

        if 'actor' in filters:

            actor_q = Q()
            for actor in filters['actor']:
                actor_q |= Q(movieactor__actor__actor_name__iexact=actor)
            queryset = queryset.filter(actor_q)

        if 'genre' in filters:

            genre_q = Q()
            for genre in filters['genre']:
                genre_q |= Q(genres__genre__iexact=genre)
            queryset = queryset.filter(genre_q)

        queryset = queryset.distinct()
        filtered_movie_ids = set(queryset.values_list('movie_id', flat=True))

        user_embedding = model.encode(user_message).tolist()
        movies_collection = chroma_client.get_collection("movies_embeddings")

        results = movies_collection.query(
            query_embeddings=[user_embedding],
            n_results=20000,
        )

        movie_ids = results["ids"][0]
        distances = results["distances"][0]

        final_movie_ids = set()

        for movie_id, distance in zip(movie_ids, distances):

            movie_id = int(movie_id)

            if movie_id in filtered_movie_ids and (movie_id, distance) not in final_movie_ids:
                final_movie_ids.add((movie_id,distance))

        final_movie_ids = sorted(final_movie_ids, key = lambda x : x[1])[:20]
        movies = [Movie.objects.get(movie_id=cur_id) for cur_id,_ in final_movie_ids]

        system_logger.info(f"Best matches for the {user_message} : {[movie.original_title for movie in movies]}")

        return render(request, "movie/search_movie.html", {"movies": movies})

    return render(request, "movie/search_movie.html")


def enter_query(request):
    """
    display search menu
    """

    return render(request, "movie/search_movie.html")


def movie_search(request):
    """
    Find the best matches for the query.

    For text query we use full text search
    For image query we use chroma db embeddings computed with Res Net for image posters in db
    """

    query = request.POST.get("query")
    image = request.FILES.get("image")  # Check if an image was uploaded

    movies = []

    if not query and not image:
        movie_ids = request.session.get("movie_ids", [])
        movies = Movie.objects.filter(movie_id__in=movie_ids)

    else:

        if query:
            relative_path = "movies/config/languages.json"
            file_path = os.path.join(settings.BASE_DIR, relative_path)

            with open(file_path, "r") as f:
                language_config = json.load(f)

            try:
                language = detect(query)
            except Exception as e:
                system_logger.error(f"Could not detect language: {e}")
                language = "english"

            pg_config = language_config.get(language, "english")

            search_query = SearchQuery(query, config=pg_config)
            search_vector = SearchVector("original_title", config=pg_config, weight="A")

            movies = (
                Movie.objects.annotate(rank=SearchRank(search_vector, search_query), similarity=TrigramSimilarity("original_title", query))  # Trigram similarity for typo tolerance
                .filter(Q(rank__gte=0.1) | Q(similarity__gte=0.3))
                .order_by("-rank", "-similarity")
            )

            movies = list(movies[:20])
            system_logger.info(f"best mathces for {query} are ': {[movie.original_title for movie in movies]}")

            request.session["movie_ids"] = [movie.movie_id for movie in movies]

        if image:

            posters_collection = chroma_client.get_collection("posters_collection")
            resnet, transform = get_model_pipeline()

            try:
                img = Image.open(image).convert("RGB")
                image_tensor = transform(img).unsqueeze(0)

                with torch.no_grad():
                    embedding = resnet(image_tensor)

                embedding = embedding.squeeze().numpy()

                results = posters_collection.query(
                    query_embeddings=[embedding],
                    n_results=20,
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

                        system_logger.info(f"ResNet Search results': {[movie.original_title for movie in matching_movies]}")

                        if matching_movies.exists():
                            movies.extend(list(matching_movies))
                        else:
                            system_logger.info(f"No movies found with the title: {title}")
                    except Exception as e:
                        system_logger.exception(f"Error retrieving movie with title {title}: {e}")

                request.session["movie_ids"] = [movie.movie_id for movie in movies]

            except UnidentifiedImageError:
                return render(request, "movie/search_movie.html", {"error": "Invalid image format"})

            except Exception as e:
                return render(
                    request,
                    "movie/search_movie.html",
                    {"error": f"Error processing image: {e}"},
                )

    paginator = Paginator(movies, 10)
    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)
    context = {"movies": page_obj}

    return render(request, "movie/search_movie.html", context=context)


def show_movie(request, movie_id):

    """
    show selected movie and display recommendations
    """

    cache_key = f"recommended_ids_{movie_id}_{request.user.id if request.user.is_authenticated else ''}"
    recommended_ids = cache.get(cache_key)


    movie = Movie.objects.get(movie_id__exact=movie_id)
    wordvec = Word2Vec.load(str(settings.MODEL_DIR))

    genres = movie.genres.all()
    genres_in_movie = genres.values_list("genre", flat=True)

    languages = movie.languages.all()
    language_in_movie = languages.values_list("language", flat=True)

    movie_actors = MovieActor.objects.filter(movie=movie).select_related("actor")
    meta_data_names = [field for field in settings.FEATURES]

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

        user = request.user
        user = user if user.is_authenticated else None

        recommended_ids = produce_recommendations(cur_row_metadata_values, metadata_rows, user_ratings, metadata_name=meta_data_names, user=user)
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
