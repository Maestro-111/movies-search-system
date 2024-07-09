
from pathlib import Path
import os

from get_clean_data import get_data
from get_clean_data import clean_text
from gensim.models import Word2Vec
from get_clean_data import get_text_vectors
from nltk.tokenize import word_tokenize


BASE_DIR = Path(__file__).resolve().parent.parent
movies_dir = 'movies'

db_path = os.path.join(BASE_DIR,movies_dir)
db_path = os.path.join(db_path, 'db.sqlite3')

model_path = os.path.join(BASE_DIR,"word2vec.model")

def prepare_text_corpus():


    txt = get_data(db_path)
    txt = [tup[0] for tup in txt]

    corpus = list(map(clean_text,txt))
    return corpus


def train_save_Word2Vec(corpus):

    model = Word2Vec(sentences=corpus, vector_size=5, window=5, min_count=20, workers=4)
    model.save(model_path)


def pipeline(train_save=False, test=False):

    corpus = prepare_text_corpus()
    tokenized_corpus = [word_tokenize(doc) for doc in corpus]

    if train_save:
        train_save_Word2Vec(tokenized_corpus)

    if test:
        model = Word2Vec.load(model_path)

        some_txt = corpus[:5]

        text_vectors = get_text_vectors(some_txt, model)

        for i, vec in enumerate(text_vectors):
            print(f"Original Text: {some_txt[i]}\n")
            print(f"Vector for text {i + 1}: {vec} : {len(vec)}")



if __name__ == '__main__':
    pipeline(train_save=True,test=False)


