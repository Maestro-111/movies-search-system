import numpy as np


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