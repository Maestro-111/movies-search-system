from populate_mixin import populate_mixin
import psycopg2
import pandas as pd


class populate_movies(populate_mixin):
    def __init__(self):
        super().__init__("movies")

    def run(self):
        conn = psycopg2.connect(
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
        )

        df = pd.read_excel(self.df_path, index_col=0)

        cursor = conn.cursor()

        # movie_id = 0

        for row in df.itertuples(index=False):
            count = len(row)
            parsed_vales = ""

            slug = row[0].lower().replace(" ", "-")
            slug = slug.replace("'", "")

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

            parsed_vales += f",'{slug}'"

            statement = f"INSERT INTO movie_movie (original_title,overview,tagline,year,movie_id,slug)" f" VALUES ({parsed_vales});"

            print(statement)

            try:
                cursor.execute(statement)
            except Exception as e:
                print(e)
                exit(1)

        # Commit changes
        conn.commit()
        conn.close()
