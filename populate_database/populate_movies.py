import pandas as pd

import os
import pandas as pd
import sqlite3



conn = sqlite3.connect('C:/movies-search-system/movies/db.sqlite3')
df = pd.read_excel('C:/movies-search-system/data/movies.xlsx',index_col=0)

cursor = conn.cursor()

movie_id = 0
for row in df.itertuples(index=False):

    count = len(row)
    parsed_vales = ""

    slug = row[0].lower().replace(" ", "-")
    slug = slug.replace("'", "")

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


    parsed_vales += f",'{slug}'"


    statement = f"INSERT INTO movie_movie (original_title,overview,tagline,year,movie_id,slug)" \
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

