import spacy
import django
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movies.settings.local")
django.setup()

MODEL_PATH = BASE_DIR / "embeddings" / "spacy_model"

from movie.models import MovieGenres, MovieActor, Movie, MovieLanguages


def train_and_save_spacy_model():


    nlp = spacy.load('en_core_web_sm')

    if "entity_ruler" not in nlp.pipe_names:
        ruler = nlp.add_pipe("entity_ruler", before="ner")
    else:
        ruler = nlp.get_pipe("entity_ruler")

    patterns = [
        {"label": "GENRE", "pattern": genre}
        for genre in MovieGenres.objects.values_list('genre', flat=True)
        if genre
    ]

    patterns.extend([
        {"label": "ACTOR", "pattern": actor_name}
        for actor_name in MovieActor.objects.values_list('actor__actor_name', flat=True).distinct()
        if actor_name
    ])

    patterns.extend([
        {"label": "YEAR", "pattern": year}
        for year in Movie.objects.values_list('year', flat=True).distinct()
        if year
    ])

    patterns.extend([
        {"label": "LANGUAGE", "pattern": language}
        for language in MovieLanguages.objects.values_list('language', flat=True).distinct()
        if language
    ])

    ruler.add_patterns(patterns)
    nlp.to_disk("spacy_model")

    print("Model saved successfully!")


if __name__ == "__main__":
    train_and_save_spacy_model()