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
        
        year = datetime.now().year
        month = datetime.now().month
        days_number = (date(year, month + 1, 1) - date(year, month, 1)).days

        date_rage_start = date.today()
        date_range_end = date_range_start + timedelta(month=1)
        date_range_step = timedelta(days=1)

        while day <= day + timedelta(days=30):

            cur.execute("""INSERT INTO day (ts) VALUES (?)""", day)

            day = timedelta(days=1)


def get_list_of_the_bridges():
    with sq.connect(DB_PATH) as con:
        cur = con.cursor()

        cur.execute("""SELECT full_title FROM bridge LEFT JOIN day ON """)
