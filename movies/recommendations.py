import numpy as np
from nltk.tokenize import word_tokenize
from django.conf import settings


def produce_recommendations_1(cur_row_metadata_values, metadata_rows):
    """

    legacy (not using)

    compute predictions ( dot products) for each cur_row_metadata_values and metadata_rows pair.

    using dot product

    """

    meta_ids, meta_matrix = zip(*metadata_rows)
    meta_matrix = np.array(meta_matrix)

    dot_products = np.dot(meta_matrix, cur_row_metadata_values)

    meta_ids = np.array(meta_ids)
    combined = np.vstack((meta_ids, dot_products)).T

    sorted_indices = np.argsort(-combined[:, 1])
    recommended_ids = combined[sorted_indices[:10], 0].astype(int)

    return recommended_ids.tolist()


def produce_recommendations(cur_row_metadata_values, metadata_rows, user_ratings, alpha=0.95):
    """
    Produce movie recommendations using cosine similarity and user ratings.
    :param cur_row_metadata_values: Array of current movie features.
    :param metadata_rows: List of tuples (movie_id, movie_features_array).
    :param user_ratings: Dictionary of movie_id to user rating.
    :param alpha: Weight factor to balance between similarity and rating (0 < alpha < 1).
    :return: List of recommended movie IDs.
    """

    """
    define matrix for all the movies (except current movie)

    Basically,
    meta_matrix =
          Feature1 Feature2 Feature3 .....
    movie1  x        x         x
    movie2  x        x         x
    movie3  x        x         x

    meta_ids are just ids of each movie
    """

    meta_ids, meta_matrix = zip(*metadata_rows)
    meta_matrix = np.array(meta_matrix)

    # Store length of each row to normalize later
    meta_matrix_norm = np.linalg.norm(meta_matrix, axis=1, keepdims=True)
    cur_row_metadata_values_norm = np.linalg.norm(cur_row_metadata_values)

    # Avoid division by zero
    meta_matrix_norm[meta_matrix_norm == 0] = 1
    if cur_row_metadata_values_norm == 0:
        cur_row_metadata_values_norm = 1

    """
    now our matrix is the same, but the same of each row is now 1 (normalized).

    We divide each row by its length for both meta_matrix (all movies except us) and cur_row_metadata_values (us)
    """

    normalized_meta_matrix = meta_matrix / meta_matrix_norm
    normalized_cur_row_metadata_values = cur_row_metadata_values / cur_row_metadata_values_norm

    # Compute cosine similarities
    cosine_similarities = np.dot(normalized_meta_matrix, normalized_cur_row_metadata_values)

    """
    cos sim = dot product between our vectors/ length product of 2 vectors (which will be 1 since normalized)
    """

    meta_ids = np.array(meta_ids)
    combined_scores = []

    """

    Combine Similarity with User Ratings:
    For each movie, combine the cosine similarity score with the user’s rating using the formula:

    combined_score= α×cosine_similarity+(1−α)×user_rating
    """

    for i, movie_id in enumerate(meta_ids):
        # Get user rating for this movie if available, otherwise default to neutral rating (e.g., 0.5)
        user_rating = user_ratings.get(movie_id, 2.5)  # get rating for a movie for a particular user. If not rating set it to 2.5 (middle)

        # Combine cosine similarity with user rating
        combined_score = alpha * cosine_similarities[i] + (1 - alpha) * user_rating
        combined_scores.append((movie_id, combined_score))

    # Sort by combined score in descending order
    combined_scores.sort(key=lambda x: -x[1])

    # Extract top 10 recommended movie IDs
    recommended_ids = [movie_id for movie_id, score in combined_scores[:10]]

    return recommended_ids


def get_average_word_vector(tokens, model):
    """Get the average word vector for a list of tokens."""

    vectors = []
    for token in tokens:
        if token in model.wv:
            vectors.append(model.wv[token])
    if vectors:
        return np.mean(vectors, axis=0)
    else:
        # Return a zero vector if no known words are found
        return np.zeros(model.vector_size)


def get_text_vectors(text: str, model):
    """Get the vector representations for a text."""

    tokens = word_tokenize(text)

    return get_average_word_vector(tokens, model)


def get_combined_features(metadata, overview, wordvec):
    """
    Combine metadata features and text features, and apply PCA transformation.
    """

    text_features = get_text_vectors(overview, wordvec)
    meta_features = np.array([getattr(metadata, feature) for feature in settings.FEATURES])
    combined_features = np.concatenate([meta_features, text_features])

    return combined_features
