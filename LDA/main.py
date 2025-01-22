import django
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movies.movies.settings")
django.setup()

from sklearn.feature_extraction.text import CountVectorizer

import re
import nltk

from nltk.corpus import stopwords

from sklearn.decomposition import LatentDirichletAllocation

from django.contrib.auth.models import User
from movie.models import MovieLanguages, UserTopicDistribution, TopicDescription


def prepare_user_documents():

    all_users = User.objects.prefetch_related(
        'playlists',
        'playlists__movie',
        'playlists__movie__languages'
    ).all()

    user_documents = {}

    # Get English language ID (assuming you have it in MovieLanguages)
    english_language = MovieLanguages.objects.get(language='English')

    for user in all_users:
        user_playlists = user.playlists.all()

        if not user_playlists:
            continue

        user_text = []

        for playlist in user_playlists:
            # Filter for only English movies
            movies = playlist.movie.filter(languages=english_language)

            if not movies:
                continue

            user_playlist_text = " ".join([
                movie.overview.strip()
                for movie in movies
                if movie.overview  # only include non-empty overviews
            ])

            if user_playlist_text:
                user_text.append(user_playlist_text)

        if user_text:
            user_documents[user.id] = " ".join(user_text)

    print("Gathered data!")

    return user_documents




def preprocess_documents(user_documents):

    vectorizer = CountVectorizer(
        max_df=0.95,
        min_df=2,
        stop_words='english'
    )

    doc_term_matrix = vectorizer.fit_transform(user_documents.values())

    print("Created Matrix")

    return doc_term_matrix, vectorizer


def get_topic_words(lda_model, vectorizer, n_words=10):
    # Get feature names (words) from vectorizer
    feature_names = vectorizer.get_feature_names_out()

    # Get topics with their top words
    topics = {}
    for topic_idx, topic in enumerate(lda_model.components_):
        # Get the top n words for this topic
        top_words_idx = topic.argsort()[:-n_words - 1:-1]
        top_words = [feature_names[i] for i in top_words_idx]
        topics[topic_idx] = top_words

    return topics



def train_lda(doc_term_matrix, n_topics=50):
    lda = LatentDirichletAllocation(
        n_components=n_topics,
        random_state=42
    )

    lda_output = lda.fit_transform(doc_term_matrix)

    print("trained LDA")

    return lda, lda_output


def train_user_movie_lda():

    user_documents = prepare_user_documents()
    doc_term_matrix, vectorizer = preprocess_documents(user_documents)

    lda_model, user_topic_distributions = train_lda(doc_term_matrix)
    topic_words = get_topic_words(lda_model, vectorizer)

    for user_id, topic_dist in zip(user_documents.keys(), user_topic_distributions):
        UserTopicDistribution.objects.update_or_create(
            user_id=user_id,
            defaults={'distribution': topic_dist.tolist()}
        )

    for topic_id, words in topic_words.items():
        TopicDescription.objects.update_or_create(
            topic_id=topic_id,
            defaults={
                'top_words': words,
            }
        )

    return lda_model, vectorizer

if __name__ == '__main__':
    # train_user_movie_lda()
    print("hello world")