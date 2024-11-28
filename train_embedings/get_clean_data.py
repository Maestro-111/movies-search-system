import sqlite3 as sq
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import numpy as np


def get_data(db_path):
    with sq.connect(db_path) as con:
        cur = con.cursor()

        cur.execute(
            """
            SELECT overview
            FROM movie_movie
        """
        )

        rows = cur.fetchall()

    return rows


def clean_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r"\d+", "", text)  # Remove numbers
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    text = re.sub(r"\s+", " ", text)  # Remove extra whitespace
    text = text.strip()  # Remove leading/trailing whitespace
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(text)
    text = " ".join([word for word in words if word not in stop_words])

    return text


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


def get_text_vectors(texts, model):
    """Get the vector representations for a list of texts."""

    vectors = []
    for text in texts:
        tokens = word_tokenize(text)
        vector = get_average_word_vector(tokens, model)
        vectors.append(vector)

    return vectors
