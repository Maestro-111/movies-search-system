import os
from pathlib import Path
import pandas as pd
from get_data import fetch_sql
import numpy as np
import joblib
from sklearn.decomposition import PCA

BASE_DIR = Path(__file__).resolve().parent.parent
movies_dir = 'movies'

db_path = os.path.join(BASE_DIR,movies_dir)
db_path = os.path.join(db_path, 'db.sqlite3')

model_path = os.path.join(BASE_DIR,"pca_model.pkl")

GENERAL = ["budget", "popularity", "year", "revenue", "runtime", "vote_average"]
GENRES = ['Foreign', 'Telescene Film Group Productions', 'Aniplex', 'Music', 'Comedy', 'Animation', 'Action', 'TV Movie', 'Sentai Filmworks',
        'Rogue State', 'Drama', 'Carousel Productions', 'Fantasy', 'Documentary',
        'Romance', 'Western', 'Odyssey Media', 'War', 'Vision View Entertainment', 'Mystery', 'The Cartel', 'Mardock Scramble Production Committee', 'Horror',
        'Thriller', 'GoHands', 'Family', 'Science Fiction', 'Adventure', 'Crime', 'History', 'BROSTA TV', 'Pulser Productions']
SPOKEN_LANGUAGES = ['Fulfulde',
                     'Czech',
                     'Bosnian',
                     'Norwegian',
                     'Latvian',
                     'French',
                     'Cantonese',
                     'Wolof',
                     'Pashto',
                     'Portuguese',
                     'Georgian',
                     'Punjabi',
                     'Malay',
                     'Azerbaijani',
                     'Slovak',
                     'Bambara',
                     'Afrikaans',
                     'Somali',
                     'Esperanto',
                     'Polish',
                     'English',
                     'Zulu',
                     'Arabic',
                     'Hebrew',
                     'Hindi',
                     'Catalan',
                     'Hausa',
                     'Italian',
                     'Slovenian',
                     'Albanian',
                     'Telugu',
                     'Swedish',
                     'Greek',
                     'Bengali',
                     'Estonian',
                     'Persian',
                     'Turkish',
                     'Romanian',
                     'Hungarian',
                     'Thai',
                     'Basque',
                     'Urdu',
                     'Icelandic',
                     'Japanese',
                     'Uzbek',
                     'Maltese',
                     'Vietnamese',
                     'German',
                     'Croatian',
                     'Russian',
                     'Serbian',
                     'Finnish',
                     'Kinyarwanda',
                     'Irish',
                     'Spanish',
                     'Lithuanian',
                     'Korean',
                     'Latin',
                     'Tamil',
                     'Bulgarian',
                     'Norwegian Bokmål',
                     'Swahili',
                     'Dutch',
                     'Danish',
                     'Galician',
                     'Welsh',
                     'Belarusian',
                     'Ukrainian',
                     'Mandarin',
                     'Kazakh',
                     'Indonesian']


FEATURES = GENERAL+GENRES+SPOKEN_LANGUAGES


def prepare_dataframe():

    maxtrix = fetch_sql(db_path,FEATURES)
    df = pd.DataFrame(data=maxtrix,columns=FEATURES)

    return df


def train_PCA(df):

    model = PCA(n_components=0.95)
    model.fit(df)
    print(
        f"current dim is: {len(model.explained_variance_ratio_)}, explained ratio: {sum(model.explained_variance_ratio_)}"
        f"")

    joblib.dump(model, model_path)
    print(f"PCA model saved to {model_path}")


def test(row,model):
    x = model.transform(row)
    print(type(x))
    print(x)


if __name__ == '__main__':
    df = prepare_dataframe()
    # r = np.array(df.iloc[0].tolist()).reshape(1,-1)
    # m = joblib.load(model_path)
    # test(r,m)
    train_PCA(df)
