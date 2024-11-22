
from populate_mixin import populate_mixin
import psycopg2
import pandas as pd

class populate_movie_actors(populate_mixin):

    def __init__(self):
        super().__init__("movie_actors")

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

        total_rows = len(df)
        rows = 0

        for index, row in enumerate(df.itertuples(index=False), start=1):

            movie_id = row.movie_id
            actor_name = row.actors.replace("'", "") if isinstance(row.actors, str) else None
            character_name = row.charaters.replace("'", "") if isinstance(row.charaters, str) else None

            rows += 1

            # Use %s for placeholders in PostgreSQL
            cursor.execute("SELECT 1 FROM movie_movie WHERE movie_id = %s", (movie_id,))
            movie_exists = cursor.fetchone()

            if movie_exists:
                cursor.execute("SELECT id FROM movie_actors WHERE actor_name = %s", (actor_name,))
                result = cursor.fetchone()

                if result:
                    actor_id = result[0]

                    # Check if the combination of movie_id and actor_id already exists
                    cursor.execute(
                        "SELECT 1 FROM movie_movieactor WHERE movie_id = %s AND actor_id = %s",
                        (movie_id, actor_id)
                    )
                    existing_entry = cursor.fetchone()

                    if not existing_entry:
                        # Insert into movie_movieactor table if not already present
                        statement = "INSERT INTO movie_movieactor (movie_id, actor_id, character_name) VALUES (%s, %s, %s);"
                        try:
                            cursor.execute(statement, (movie_id, actor_id, character_name))
                            # Print progress
                            print(f"Progress: {int((index / total_rows) * 100)}% - Rows added: {rows}")
                        except Exception as e:
                            print(e)
                            exit(1)
                    else:
                        print(f"Entry for movie_id {movie_id} and actor_id {actor_id} already exists. Skipping...")
                else:
                    print(f"Actor '{actor_name}' not found in the database.")
            else:
                print(f"Movie ID {movie_id} not found in the movies table. Skipping...")

        # Commit changes
        conn.commit()
        conn.close()

        # Final summary
        print(f"Total rows added: {rows} out of {total_rows}")

