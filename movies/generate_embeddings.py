import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movies.settings")
django.setup()

from sentence_transformers import SentenceTransformer
from movie.models import Movie, MovieEmbedding
from chroma_db import movies_collection

model = SentenceTransformer('all-MiniLM-L6-v2')


def delete_existing_embeddings():

    movies_collection.delete(where={"movie_id": {"$gt": -1}})
    print("Deleted all existing embeddings from ChromaDB collection.")


def generate_and_save_embeddings():

    for movie in Movie.objects.all():

        text = (
            f"{movie.original_title}, a {', '.join([genre.genre for genre in movie.genres.all()])} movie "
            f"in {', '.join([language.language for language in movie.languages.all()])} from {movie.year}. "
            f"{movie.overview}"
        )

        embedding = model.encode(text).tolist()

        movies_collection.add(
            documents=[text],
            metadatas=[{"movie_id": movie.movie_id, "title": movie.original_title}],
            embeddings=[embedding],
            ids=[str(movie.movie_id)]
        )
        print(f"Added embedding for movie: {movie.original_title}")

if __name__ == "__main__":
    delete_existing_embeddings()
    generate_and_save_embeddings()



