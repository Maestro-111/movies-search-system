import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

from sklearn.model_selection import train_test_split

import torch
from torch.utils.data import Dataset


def create_df_chunks(path):
    df = pd.read_excel(path)

    count_users = len(df["User"].unique())
    count_ratings = len(df["Rating"].unique())
    unique_movies = df["Movie"].unique()

    train_data, temp_data = train_test_split(df, test_size=0.3, random_state=42)
    val_data, test_data = train_test_split(temp_data, test_size=0.5, random_state=42)

    print(f"Train size: {len(train_data)}, Validation size: {len(val_data)}, Test size: {len(test_data)}")

    return train_data, val_data, test_data, unique_movies, [count_users, count_ratings]


class MovieDataset(Dataset):
    def __init__(self, data, user_encoder=None, text_embeddings=None):
        """
        Args:
            data: pandas DataFrame containing the data.
            user_encoder: Optional, a dictionary mapping user IDs to unique indices.
            text_embeddings: A dictionary mapping movie IDs to their text embeddings.
        """
        self.data = data

        # Create a user encoder if not provided
        if user_encoder is None:
            self.user_encoder = {user: idx for idx, user in enumerate(data["User"].unique())}
        else:
            self.user_encoder = user_encoder

        # Ensure text embeddings are provided
        if text_embeddings is None:
            raise ValueError("A text_embeddings dictionary must be provided.")
        self.text_embeddings = text_embeddings

        # Map users to indices and retrieve movie embeddings
        self.users = data["User"].map(self.user_encoder).values
        self.movies = torch.tensor([self.text_embeddings[movie] for movie in data["Movie"]], dtype=torch.float32)
        self.ratings = torch.tensor(data["Rating"].values, dtype=torch.float32)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        """
        Returns:
            user: User index.
            movie: Movie embedding (vector).
            rating: Rating (target).
        """
        user = self.users[idx]
        movie = self.movies[idx]
        rating = self.ratings[idx]
        return torch.tensor(user, dtype=torch.long), movie, rating
