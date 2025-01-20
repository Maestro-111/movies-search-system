import pandas as pd
import psycopg2
from dotenv import load_dotenv, find_dotenv
from populatemixin import PopulateMixin

load_dotenv(find_dotenv())


class PopulateActors(PopulateMixin):
    def __init__(self):
        super().__init__("movie_actors")

    def run(self):
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
        )
        df = pd.read_excel(self.df_path, index_col=0)

        # Extract unique actors
        df = df[["actors"]].drop_duplicates()
        cursor = conn.cursor()

        for row in df.itertuples(index=False):
            count = len(row)
            parsed_values = ""

            for value in row:
                if count == 1:
                    if isinstance(value, str):
                        value = value.replace("'", "")
                        parsed_values += f"'{value}'"
                    else:
                        parsed_values += str(value)
                else:
                    if isinstance(value, str):
                        value = value.replace("'", "")
                        parsed_values += f"'{value}', "
                    else:
                        parsed_values += str(value) + ", "

                count -= 1

            statement = f"INSERT INTO movie_actors (actor_name)" f" VALUES ({parsed_values});"

            print(statement)

            try:
                cursor.execute(statement)
            except Exception as e:
                print(e)
                conn.rollback()  # Rollback in case of an error
                exit(1)

        # Commit changes
        conn.commit()
        conn.close()
