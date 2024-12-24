import torch
import torch.nn as nn


class RecommendationModel(nn.Module):
    def __init__(self, n_users, user_embedding_dim, movie_text_embedding_dim, n_classes, dropout_rate=0.5):
        super(RecommendationModel, self).__init__()

        # User embedding layer
        self.user_embedding = nn.Embedding(num_embeddings=n_users, embedding_dim=user_embedding_dim)

        # Fully connected layers
        self.fc1 = nn.Linear(user_embedding_dim + movie_text_embedding_dim, 256)
        self.bn1 = nn.BatchNorm1d(256)
        self.dropout1 = nn.Dropout(p=dropout_rate)

        self.fc2 = nn.Linear(256, 128)
        self.bn2 = nn.BatchNorm1d(128)
        self.dropout2 = nn.Dropout(p=dropout_rate)

        self.fc3 = nn.Linear(128, 64)
        self.bn3 = nn.BatchNorm1d(64)
        self.dropout3 = nn.Dropout(p=dropout_rate)

        self.fc4 = nn.Linear(64, 32)
        self.bn4 = nn.BatchNorm1d(32)
        self.dropout4 = nn.Dropout(p=dropout_rate)

        self.fc5 = nn.Linear(32, 16)
        self.bn5 = nn.BatchNorm1d(16)
        self.dropout5 = nn.Dropout(p=dropout_rate)

        self.output = nn.Linear(16, n_classes)

    def forward(self, user, movie):
        # Get user embedding
        user_embedded = self.user_embedding(user)  # Shape: (batch_size, user_embedding_dim)

        # Concatenate user embedding with movie text embedding
        x = torch.cat([user_embedded, movie], dim=1)  # Shape: (batch_size, user_embedding_dim + text_embedding_dim)

        # Pass through fully connected layers
        x = self.fc1(x)
        x = self.bn1(x)
        x = torch.relu(x)
        x = self.dropout1(x)

        x = self.fc2(x)
        x = self.bn2(x)
        x = torch.relu(x)
        x = self.dropout2(x)

        x = self.fc3(x)
        x = self.bn3(x)
        x = torch.relu(x)
        x = self.dropout3(x)

        x = self.fc4(x)
        x = self.bn4(x)
        x = torch.relu(x)
        x = self.dropout4(x)

        x = self.fc5(x)
        x = self.bn5(x)
        x = torch.relu(x)
        x = self.dropout5(x)

        x = self.output(x)

        return x
