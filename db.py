import sqlite3 as sq
from datetime import date, timedelta, datetime





def init_db():
    with sq.connect(DB_PATH) as con:
        cur = con.cursor()

        cur.execute(BRIDGE_CREATE)
        cur.execute(DAY_CREATE)
        cur.execute(OPENING_CREATE)


def init_bridges(data):
    with sq.connect(DB_PATH) as con:
        cur = con.cursor()

        for key, value in data.items():
            params = [key, value]
            cur.execute(INSERT_BRIDGE, params)


def init_days():
    with sq.connect(DB_PATH) as con:
        cur = con.cursor()

        date_range = date.today() + timedelta(month=1)

        for day in date_range:

            cur.execute("""INSERT INTO day (ts) VALUES (?)""", day)


def get_list_of_the_bridges():
    with sq.connect(DB_PATH) as con:
        cur = con.cursor()

        cur.execute("""SELECT full_title FROM bridge LEFT JOIN day ON """)
