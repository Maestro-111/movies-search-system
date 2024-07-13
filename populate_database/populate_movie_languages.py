import pandas as pd

import os
import pandas as pd
import sqlite3

conn = sqlite3.connect('C:/movies-search-system/movies/db.sqlite3')
df = pd.read_excel('C:/movies-search-system/data/language_movies.xlsx',index_col=0)

cursor = conn.cursor()

for row in df.itertuples(index=False):

    count = len(row)
    parsed_vales = ""

    for value in row:

        if count == 1:
            if isinstance(value, str):
                value = value.replace("'", "")
                parsed_vales += (f"'{value}'")
            else:
                parsed_vales += (str(value))
        else:
            if isinstance(value, str):
                value = value.replace("'", "")
                parsed_vales += (f"'{value}'" + ', ')
            else:
                parsed_vales += (str(value) + ', ')


        count -= 1

    statement = f"INSERT INTO movie_movie_languages (movie_id,movielanguages_id)" \
                f" VALUES ({parsed_vales});"

    print(statement)

    try:
        cursor.execute(statement)
    except Exception as e:
        print(e)
        exit(1)

# Commit changes
conn.commit()

conn.close()
