import numpy as np
from nltk.tokenize import word_tokenize
from django.conf import settings

def produce_recommendations_1(cur_row_metadata_values, metadata_rows):

    """
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


def produce_recommendations(cur_row_metadata_values, metadata_rows):

    """

    using cosine sim

    """

    meta_ids, meta_matrix = zip(*metadata_rows)
    meta_matrix = np.array(meta_matrix)

    # Normalize the metadata rows and the current row values
    meta_matrix_norm = np.linalg.norm(meta_matrix, axis=1, keepdims=True)
    cur_row_metadata_values_norm = np.linalg.norm(cur_row_metadata_values)

    # Avoid division by zero
    meta_matrix_norm[meta_matrix_norm == 0] = 1
    if cur_row_metadata_values_norm == 0:
        cur_row_metadata_values_norm = 1

    normalized_meta_matrix = meta_matrix / meta_matrix_norm
    normalized_cur_row_metadata_values = cur_row_metadata_values / cur_row_metadata_values_norm

    # Compute cosine similarities
    cosine_similarities = np.dot(normalized_meta_matrix, normalized_cur_row_metadata_values)

    meta_ids = np.array(meta_ids)
    combined = np.vstack((meta_ids, cosine_similarities)).T

    # Sort by cosine similarity in descending order
    sorted_indices = np.argsort(-combined[:, 1])
    recommended_ids = combined[sorted_indices[:10], 0].astype(int)

    return recommended_ids.tolist()


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

def get_text_vectors(text:str, model):

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
