import psycopg2
from dotenv import load_dotenv, find_dotenv
from .populatemixin import PopulateMixin

load_dotenv(find_dotenv())


# class populate_user_profile(populate_mixin):
#
#     def __init__(self, user_id):
#
#         super().__init__()
#         self.user_id = user_id
#
#     def run(self):
#         conn = psycopg2.connect(
#             dbname=self.db_name,
#             user=self.db_user,
#             password=self.db_password,
#             host=self.db_host,
#             port=self.db_port,
#         )
#
#         cursor = conn.cursor()
#
#         # Query all users
#         cursor.execute("SELECT id FROM auth_user")
#         users = cursor.fetchall()
#
#         # Insert a profile for each user
#         for user in users:
#             user_id = user[0]
#             cursor.execute(
#                 "INSERT INTO users_profile (user_id) VALUES (%s) ON CONFLICT DO NOTHING",
#                 (user_id,),
#             )
#
#         conn.commit()
#         cursor.close()
#         conn.close()

class PopulateUserProfile(PopulateMixin):

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

