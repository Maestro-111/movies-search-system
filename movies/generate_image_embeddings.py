import pandas as pd
from chroma_db import posters_collection

import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import requests
from io import BytesIO


def get_model_pipeline():
    resnet = models.resnet50(pretrained=True)
    resnet.eval()

    resnet = torch.nn.Sequential(*list(resnet.children())[:-1])

    transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )

    return resnet, transform


def delete_existing_embeddings():
    try:
        posters_collection.delete(where={"*": "*"})  # Matches all documents
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
    df = pd.read_csv("data/imdb_top_1000.csv")

    resnet, transform = get_model_pipeline()

    for index, row in df.iterrows():
        url = row.Poster_Link
        image_embedding = get_embedding(url, resnet, transform)

        if image_embedding is not None:
            posters_collection.add(
                documents=[row.Series_Title],
                metadatas=[{"title": row.Series_Title}],
                embeddings=[image_embedding],
                ids=[f"{row.Series_Title}_{index}"],
            )


if __name__ == "__main__":
    delete_existing_embeddings()
    generate_and_save_embeddings()

    print(posters_collection.count())
