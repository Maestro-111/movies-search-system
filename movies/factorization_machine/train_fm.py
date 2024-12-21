import pandas as pd

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

import os


from sklearn.model_selection import train_test_split

from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer


def prepare_data(path):
    df = pd.read_excel(path)

    y = df["Rating"]
    X = df.drop("Rating", axis=1)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    categorical_cols = ["User", "Movie"]
    numerical_cols = df.columns.difference(categorical_cols + ["Rating"])

    preprocessor = ColumnTransformer(transformers=[("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols), ("num", "passthrough", numerical_cols)])

    X_train = preprocessor.fit_transform(X_train)
    X_test = preprocessor.transform(X_test)

    return X_train, X_test, y_train, y_test


def train_test_output():
    pass


X_train, X_test, y_train, y_test = prepare_data(path=os.path.join(BASE_DIR, "movies/data/ratings_data.xlsx"))
