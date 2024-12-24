import torch
import numpy as np

from pathlib import Path
import os

from create_data import create_df_chunks, MovieDataset
from torch.utils.data import DataLoader

from create_model import RecommendationModel

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
from transformers import AutoTokenizer, AutoModel


BATCH = 16
BASE_DIR = Path(__file__).resolve().parent.parent.parent
USER_DIM = 10
MOVIE_DIM = 10
EPOCHS = 50


tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")


def encode_text(text):
    global MOVIE_DIM

    tokens = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)

    with torch.no_grad():
        output = model(**tokens)

    embedding = output.last_hidden_state[:, 0, :].squeeze().numpy()

    MOVIE_DIM = embedding.shape[0]
    return embedding


def get_batches():
    train_data, val_data, test_data, unique_movies, stats = create_df_chunks(os.path.join(BASE_DIR, "movies/data/new_ratings_data.xlsx"))

    text_embeddings = {movie: encode_text(movie) for movie in unique_movies}

    print(MOVIE_DIM)

    train_dataset = MovieDataset(train_data, text_embeddings=text_embeddings)
    val_dataset = MovieDataset(val_data, user_encoder=train_dataset.user_encoder, text_embeddings=text_embeddings)
    test_dataset = MovieDataset(test_data, user_encoder=train_dataset.user_encoder, text_embeddings=text_embeddings)

    train_loader = DataLoader(train_dataset, batch_size=BATCH, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH, shuffle=True)

    print(stats)

    return train_loader, val_loader, test_loader, stats


def plot_confusion_matrix(y_true, y_pred, class_names):
    """
    Plots a confusion matrix using Matplotlib and Seaborn.

    Args:
        y_true (list or np.array): Ground truth (actual) labels.
        y_pred (list or np.array): Predicted labels.
        class_names (list): List of class names corresponding to labels.
    """
    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred)

    # Normalize confusion matrix (optional)
    cm_normalized = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]

    # Create a heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm_normalized, annot=True, fmt=".2f", cmap="Blues", xticklabels=class_names, yticklabels=class_names)
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.show()


def train_model(train_loader, val_loader, test_loader, stats):
    count_users, count_ratings = stats

    model = RecommendationModel(count_users, USER_DIM, MOVIE_DIM, count_ratings)
    loss_fn = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    train_losses, val_losses = [], []
    train_accuracies, val_accuracies = [], []

    # Training Loop
    for epoch in range(EPOCHS):
        model.train()  # Set model to training mode
        train_loss, train_correct, total_train = 0.0, 0, 0

        for user, movie, rating in train_loader:
            user = user.to(torch.long)
            movie = movie.to(torch.long)

            target = (rating - 1).to(torch.long)  # Convert ratings 1-5 to 0-4

            # Forward pass
            outputs = model(user, movie)
            loss = loss_fn(outputs, target)

            # Backward pass and optimization
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            # Record metrics
            train_loss += loss.item()
            _, predicted = torch.max(outputs, dim=1)
            train_correct += (predicted == target).sum().item()
            total_train += target.size(0)

        # Calculate and store train metrics
        avg_train_loss = train_loss / len(train_loader)
        train_accuracy = train_correct / total_train
        train_losses.append(avg_train_loss)
        train_accuracies.append(train_accuracy)

        # Validation Loop
        model.eval()  # Set model to evaluation mode
        val_loss, val_correct, total_val = 0.0, 0, 0

        with torch.no_grad():
            for user, movie, rating in val_loader:
                user = user.to(torch.long)
                movie = movie.to(torch.float32)
                target = (rating - 1).to(torch.long)

                outputs = model(user, movie)
                loss = loss_fn(outputs, target)

                # Record metrics
                val_loss += loss.item()
                _, predicted = torch.max(outputs, dim=1)
                val_correct += (predicted == target).sum().item()
                total_val += target.size(0)

        # Calculate and store validation metrics
        avg_val_loss = val_loss / len(val_loader)
        val_accuracy = val_correct / total_val
        val_losses.append(avg_val_loss)
        val_accuracies.append(val_accuracy)

        # Print metrics for this epoch
        print(f"Epoch [{epoch + 1}/{EPOCHS}]")
        print(f"Train Loss: {avg_train_loss:.4f}, Train Accuracy: {train_accuracy:.4f}")
        print(f"Val Loss: {avg_val_loss:.4f}, Val Accuracy: {val_accuracy:.4f}")

    # Test Loop
    test_correct, total_test = 0, 0
    all_targets, all_predictions = [], []

    with torch.no_grad():
        for user, movie, rating in test_loader:
            user = user.to(torch.long)
            movie = movie.to(torch.float32)
            target = (rating - 1).to(torch.long)

            outputs = model(user, movie)
            _, predicted = torch.max(outputs, dim=1)

            # Record predictions and targets
            all_targets.extend(target.cpu().numpy())
            all_predictions.extend(predicted.cpu().numpy())

            test_correct += (predicted == target).sum().item()
            total_test += target.size(0)

    # Calculate test accuracy
    test_accuracy = test_correct / total_test
    print(f"Test Accuracy: {test_accuracy:.4f}")

    # Confusion Matrix
    cm = confusion_matrix(all_targets, all_predictions)
    plot_confusion_matrix(all_targets, all_predictions, ["Rating 1", "Rating 2", "Rating 3", "Rating 4", "Rating 5"])

    print("Confusion Matrix:")
    print(cm)

    torch.save(model.state_dict(), os.path.join(BASE_DIR, "movies/recommendation_model.pth"))

    return {
        "train_losses": train_losses,
        "train_accuracies": train_accuracies,
        "val_losses": val_losses,
        "val_accuracies": val_accuracies,
        "test_accuracy": test_accuracy,
        "confusion_matrix": cm,
    }


def main():
    train_loader, val_loader, test_loader, stats = get_batches()
    train_model(train_loader, val_loader, test_loader, stats)


if __name__ == "__main__":
    main()
