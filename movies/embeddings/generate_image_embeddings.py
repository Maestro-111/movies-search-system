import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movies.settings")
django.setup()


import pandas as pd
from chroma_db import posters_collection

import torch

from PIL import Image
import requests
from io import BytesIO

import re

from django.db.models import Q
from movie.models import Movie

from model_pipeline import get_model_pipeline


def delete_existing_embeddings():
    try:
        posters_collection.delete(where={"dummy_check": {"$gt": -1}})
        print("Deleted all existing embeddings from ChromaDB collection.")
    except Exception as e:
        print(f"Error during deletion: {e}")


def fetch_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content)).convert("RGB")


def get_embedding(image_url, resnet, transform):
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert("RGB")
        image_tensor = transform(image).unsqueeze(0)  # Add batch dimension
        with torch.no_grad():
            embedding = resnet(image_tensor)
        return embedding.squeeze().numpy()
    except Exception as e:
        print(f"Error fetching or processing image from {image_url}: {e}")
        return None


def generate_and_save_embeddings():
    with open("data/posters.csv", encoding="utf-8", errors="replace") as f:
        df = pd.read_csv(f)

    resnet, transform = get_model_pipeline()

    for index, row in df.iterrows():
        movie_name = re.findall(r"^(.*) \(\d+\)", row.Title)
        year = re.findall(r"\((\d+)\)", row.Title)

        if not movie_name or not year:
            print(f"Invalid title format: {row.Title}")
            continue

        movie_name = movie_name[0].strip()
        year = int(year[0])

        print(index, movie_name, year)

        if Movie.objects.filter(Q(original_title=movie_name) & Q(year=year)).exists():
            url = row.Poster
            image_embedding = get_embedding(url, resnet, transform)

            if image_embedding is not None:
                posters_collection.add(
                    documents=[row.Title],
                    metadatas=[{"title": row.Title, "dummy_check": 0}],
                    embeddings=[image_embedding],
                    ids=[f"{row.Title}_{index}"],
                )


if __name__ == "__main__":
    print("hello world")
    # delete_existing_embeddings()
    # generate_and_save_embeddings()
