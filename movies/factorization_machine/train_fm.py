import pandas as pd
import os
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer

from .XGB_ranker import MovieRankingXGB

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def prepare_data(path):
    # Load data
    df = pd.read_excel(path)

    # df = df.iloc[:5000]
    df["User"] = df["User"].astype("category")

    # Adjust ratings to 0-4 instead of 1-5
    df["Rating"] = df["Rating"] - 1

    # Split features and target
    y = df["Rating"]
    X = df.drop("Rating", axis=1)

    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    categorical_cols = ["User", "Movie"]
    numerical_cols = X.columns.difference(categorical_cols)

    # Preprocessing pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
            ("num", "passthrough", numerical_cols),
        ]
    )

    return X_train, X_test, y_train, y_test, preprocessor



def train_test_output(path):

    df = pd.read_excel(path)
    target = "Rating"

    model = MovieRankingXGB(
        df = df,
        target=target,
        test_size = 0.2,
        val_size=0.2,
        iters=100,
        save=True,
    )

    model.train()



if __name__ == "__main__":
    train_test_output(os.path.join(BASE_DIR, "movies/data/ratings_data.xlsx"))
