import django
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movies.movies.settings")
django.setup()

from sklearn.feature_extraction.text import CountVectorizer

import re


from nltk import pos_tag, word_tokenize,PorterStemmer
from nltk.stem import WordNetLemmatizer

from nltk.corpus import stopwords

from sklearn.decomposition import LatentDirichletAllocation

from django.contrib.auth.models import User
from movie.models import MovieLanguages, UserTopicDistribution, TopicDescription

import string

N = 350

"""

Train LDA on user/playlist

"""


stopwords = set(stopwords.words('english'))
stemmer = PorterStemmer()

lemmatizer = WordNetLemmatizer()
regex = re.compile('[%s]' % re.escape(string.punctuation+"—”“’"+"0123456789"))

def prepare_user_documents():

    all_users = User.objects.prefetch_related(
        'playlists',
        'playlists__movie',
        'playlists__movie__languages'
    ).all()

    user_documents = {}
    english_language = MovieLanguages.objects.get(language='English')

    for user in all_users:

        user_playlists = user.playlists.all()

        if not user_playlists:
            continue

        for playlist in user_playlists:
            movies = playlist.movie.filter(languages=english_language)

            if not movies:
                continue

            user_playlist_text = " ".join([
                clean_text(movie.overview.strip())
                for movie in movies
                if movie.overview
            ])


            if user_playlist_text:
                user_documents[str(user.id)+"!"+str(playlist.id)] = user_playlist_text

    i = 5
    for user in user_documents:

        if not i:
            break

        i -= 5

    print("Gathered data for all users!")

    return user_documents



def clean_text(text:str):

    text = regex.sub('', text)

    text = (token.strip().lower() for token in text.split()
            if token.strip().lower() not in stopwords
            and len(token.strip()) >= 3  # minimum 3 letters
            and token.strip().isalpha()  # only alphabetic characters
    )

    tokens = word_tokenize(" ".join(list(text)))
    tagged = pos_tag(tokens)

    cleaned_tokens = []

    for word, tag in tagged:
        word = word.strip().lower()
        if word not in stopwords and len(word) >= 3:
            # Convert POS tag to WordNet POS tag
            pos = 'n'  # default to noun
            if tag.startswith('VB'):  # verb
                pos = 'v'
            elif tag.startswith('JJ'):  # adjective
                pos = 'a'
            elif tag.startswith('RB'):  # adverb
                pos = 'r'

            lemma = lemmatizer.lemmatize(word, pos=pos)

            if lemma:
                cleaned_tokens.append(lemma)

    return " ".join(cleaned_tokens)




def preprocess_documents(user_documents):

    vectorizer = CountVectorizer(
        max_df=0.98,
        min_df=1,
        stop_words='english',
        token_pattern=r'(?u)\b[a-zA-Z]{3,}\b',
        ngram_range=(1, 3)
    )

    doc_term_matrix = vectorizer.fit_transform(user_documents.values())

    print("Created Matrix")

    return doc_term_matrix, vectorizer


def get_topic_words(lda_model, vectorizer, n_words=10):

    feature_names = vectorizer.get_feature_names_out()

    topics = {}

    for topic_idx, topic in enumerate(lda_model.components_):

        top_words_idx = topic.argsort()[:-n_words - 1:-1]

        top_words = [feature_names[i] for i in top_words_idx]
        topics[topic_idx] = top_words

    return topics



def train_lda(doc_term_matrix):

    lda = LatentDirichletAllocation(
        n_components=N,
        max_iter=20
    )

    lda_output = lda.fit_transform(doc_term_matrix)

    print("trained LDA")

    return lda, lda_output


import matplotlib.pyplot as plt


def plot_perplexity_scores(doc_term_matrix):

    topic_numbers = range(1,120,5)
    perplexities = []

    for n_topics in topic_numbers:
        lda = LatentDirichletAllocation(n_components=n_topics, max_iter=20)
        lda.fit(doc_term_matrix)
        perplexity = lda.perplexity(doc_term_matrix)
        perplexities.append(perplexity)
        print(f'Topics: {n_topics}, Perplexity: {perplexity}')


    plt.plot(topic_numbers, perplexities, 'bo-')
    plt.xlabel('Number of Topics')
    plt.ylabel('Perplexity Score')
    plt.title('LDA Topic Number vs Perplexity')
    plt.savefig('perplexity_plot.png')
    plt.close()



def train_user_movie_lda():

    user_documents = prepare_user_documents()
    doc_term_matrix, vectorizer = preprocess_documents(user_documents)

    sparsity = (doc_term_matrix.nnz / (doc_term_matrix.shape[0] * doc_term_matrix.shape[1])) * 100

    print(f"Matrix sparsity: {sparsity}%")

    plot_perplexity_scores(doc_term_matrix)

    lda_model, user_topic_distributions = train_lda(doc_term_matrix)
    topic_words = get_topic_words(lda_model, vectorizer)

    UserTopicDistribution.objects.all().delete()
    TopicDescription.objects.all().delete()

    for id, topic_dist in zip(user_documents.keys(), user_topic_distributions):

        user_id,playlist_id = id.split("!")

        UserTopicDistribution.objects.update_or_create(
            user_id=user_id,
            playlist_id=playlist_id,
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

    train_user_movie_lda()
    print("hello world")