from populate_mixin import populate_mixin
import psycopg2
import pandas as pd
from pathlib import Path
import os



class populate_movies(populate_mixin):


    def __init__(self):
        super().__init__("movies")
        self.base_dir = Path(__file__).resolve().parent.parent

    def run(self):

        conn = psycopg2.connect(
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
        )

        df = pd.read_excel(self.df_path, index_col=0)



        with open(os.path.join(self.base_dir,"movies/data/posters.csv"), encoding="utf-8", errors="replace") as f:
            urls_df = pd.read_csv(f)

        cursor = conn.cursor()

        for row in df.itertuples(index=False):

            count = len(row)
            parsed_vales = ""

            slug = row[0].lower().replace(" ", "-")
            slug = slug.replace("'", "")

            year =  str(row.year).strip()
            movie_name = row.original_title.lower().strip()

            cur_url = urls_df[urls_df["Title"].str.lower()== movie_name+" "+"("+year+")"]

            if cur_url.shape[0] != 1:
                cur_url = None
            else:
                cur_url = cur_url["Poster"].iloc[0]

            for value in row:

                if count == 1:
                    if isinstance(value, str):
                        value = value.replace("'", "")
                        parsed_vales += f"'{value}'"
                    else:
                        parsed_vales += str(value)
                else:
                    if isinstance(value, str):
                        value = value.replace("'", "")
                        parsed_vales += f"'{value}'" + ", "
                    else:
                        parsed_vales += str(value) + ", "

                count -= 1

            parsed_vales += f",'{slug}', '{cur_url}'"

            statement = f"""
            INSERT INTO movie_movie (original_title, overview, tagline, year, movie_id, slug, movie_url) 
            VALUES ({parsed_vales})
            ON CONFLICT (movie_id) 
            DO UPDATE SET 
                original_title = EXCLUDED.original_title,
                overview = EXCLUDED.overview,
                tagline = EXCLUDED.tagline,
                year = EXCLUDED.year,
                slug = EXCLUDED.slug,
                movie_url = EXCLUDED.movie_url;
            """

            print(statement)

            try:
                cursor.execute(statement)
            except Exception as e:
                print(e)
                exit(1)

        # Commit changes
        conn.commit()
        conn.close()


if __name__ == "__main__":
    movies= populate_movies()
    movies.run()