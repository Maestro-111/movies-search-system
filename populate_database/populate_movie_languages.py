
import pandas as pd
import sqlite3
from pathlib import Path

class populate_movie_languages:


    BASE_DIR = Path(__file__).resolve().parent.parent

    def __init__(self):

        self.database_path = self.BASE_DIR / "movies" / "db.sqlite3"
        self.df_path = self.BASE_DIR / "movies" / "data" / "language_movies.xlsx"

    def run(self):

        conn = sqlite3.connect(self.database_path)
        df = pd.read_excel(self.df_path, index_col=0)

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
