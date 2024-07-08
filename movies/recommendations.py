import numpy as np
from nltk.tokenize import word_tokenize

def produce_recommendations(cur_row_metadata_values, metadata_rows):

    """
    busines logic

    """

    dot_products = []

    for meta_id, meta_row in metadata_rows:
        dot_product = np.dot(cur_row_metadata_values, meta_row)
        dot_products.append([meta_id, dot_product])

    recommended_ids = [movie_id for (movie_id, dot_product) in
                       sorted(dot_products, key=lambda x: x[1], reverse=True)[:10]]

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

def get_text_vectors(text:str, model):

    """Get the vector representations for a text."""

    tokens = word_tokenize(text)

    return get_average_word_vector(tokens, model)
