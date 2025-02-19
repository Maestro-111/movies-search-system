import psycopg2
from dotenv import load_dotenv, find_dotenv
from .populatemixin import PopulateMixin

load_dotenv(find_dotenv())

class PopulateUserProfile(PopulateMixin):

    """
    Should not be used in main.py.
    Instead, use it when user is registered (for user we create profile)
    """


    def __init__(self, user_id):

        super().__init__()
        self.user_id = user_id

    def run(self):
        conn = psycopg2.connect(
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
        )

        cursor = conn.cursor()

        cursor.execute(
                "INSERT INTO users_profile (user_id) VALUES (%s) ON CONFLICT DO NOTHING",
            (self.user_id,),
        )

        conn.commit()
        cursor.close()
        conn.close()

