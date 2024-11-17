import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movies.settings")
django.setup()

from sentence_transformers import SentenceTransformer
from movie.models import Movie, MovieActor
from chroma_db import movies_collection,chroma_client

model = SentenceTransformer('all-MiniLM-L6-v2')


def delete_existing_embeddings():

    movies_collection.delete(where={"movie_id": {"$gt": -1}})
    print("Deleted all existing embeddings from ChromaDB collection.")


def generate_and_save_embeddings():

    for movie in Movie.objects.all():

        print(movie.movie_id)

        movie_actors = MovieActor.objects.filter(movie=movie).select_related('actor')

        actors = ", ".join([movie_actor.actor.actor_name or "Unknown Actor" for movie_actor in movie_actors])
        charaters = ", ".join([movie_actor.character_name or "Unknown Character" for movie_actor in movie_actors])

        text = (
            f"{movie.original_title}, a {', '.join([genre.genre for genre in movie.genres.all()])} movie "
            f"in {', '.join([language.language for language in movie.languages.all()])} from {movie.year or 'an unknown year'}. "
            f"Actors: {actors}. "
            f"Characters: {charaters}. "
            f"{movie.overview or ''}"
        )

        embedding = model.encode(text).tolist()

        movies_collection.add(
            documents=[text],
            metadatas=[{"movie_id": movie.movie_id, "title": movie.original_title or "Unknown Title"}],
            embeddings=[embedding],
            ids=[str(movie.movie_id)]
        )
        print(f"Added embedding for movie: {movie.original_title}")
        print(text)
        print()



if __name__ == "__main__":

    delete_existing_embeddings()
    generate_and_save_embeddings()



