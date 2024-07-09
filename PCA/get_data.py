import sqlite3 as sq
from pathlib import Path
import os
import re
import numpy as np

def fetch_sql(db_path,features_list):

    """
    Get features_list data from metadata table

    """

    with sq.connect(db_path) as con:
        cur = con.cursor()

        st = ""

        for indx, feature in enumerate(features_list):

            if len(feature.split()) > 1 or feature == 'Foreign':
                st += '\"' + feature + '\"'
                st = st+',' if indx < len(features_list)-1 else st
            else:
                st += feature
                st = st + ',' if indx < len(features_list) - 1 else st

        query = "SELECT "+st+" FROM movie_moviemetadata;"

        cur.execute(query)

        rows = cur.fetchall()

    return rows