import pandas as pd
import os
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
    roc_auc_score
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def prepare_data(path):
    # Load data
    df = pd.read_excel(path)

    # Split features and target
    y = df["Rating"]
    X = df.drop("Rating", axis=1)

    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Define categorical and numerical columns
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

def train_test_output():
    # Prepare data
    X_train, X_test, y_train, y_test, preprocessor = prepare_data(
        path=os.path.join(BASE_DIR, "movies/data/ratings_data.xlsx")
    )

    # Use a classification model
    model = RandomForestClassifier(random_state=42, n_estimators=100)

    # Create pipeline
    pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("classifier", model)])
    pipeline.fit(X_train, y_train)

    # Predictions
    y_pred = pipeline.predict(X_test)
    y_pred_proba = pipeline.predict_proba(X_test)  # Probabilities for ROC-AUC

    # Metrics
    acc = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="weighted")  # Weighted for multiclass
    recall = recall_score(y_test, y_pred, average="weighted")
    f1 = f1_score(y_test, y_pred, average="weighted")
    auc = roc_auc_score(y_test, y_pred_proba, multi_class="ovr")  # One-vs-rest for multiclass

    print("Model Performance:")
    print(f"Accuracy: {acc:.2f}")
    print(f"Precision (Weighted): {precision:.2f}")
    print(f"Recall (Weighted): {recall:.2f}")
    print(f"F1 Score (Weighted): {f1:.2f}")
    print(f"ROC-AUC (OvR): {auc:.2f}")

    cm = confusion_matrix(y_test, y_pred)
    print("\nConfusion Matrix:")
    print(cm)

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

if __name__ == "__main__":
    train_test_output()

