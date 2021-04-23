import sqlite3 as sq
from datetime import date, timedelta, datetime


def creating_the_tables_templates():
    with sq.connect('bridges_database.db') as con:
        cur = con.cursor()

        # creating tables for data
        cur.execute("""CREATE TABLE IF NOT EXISTS bridge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        full_title TEXT NOT NULL)""")

        cur.execute("""CREATE TABLE IF NOT EXISTS day (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts DATE NOT NULL DEFAULT CURRENT_DATE)""")

        cur.execute("""CREATE TABLE IF NOT EXISTS opening (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        started_at TIME NOT NULL,
        closed_at TIME NOT NULL,
        FOREIGN KEY (id) REFERENCES day (id),
        FOREIGN KEY (id) REFERENCES bridge (id))""")


def fill_the_bridge_table(data):
    with sq.connect('bridges_database.db') as con:
        cur = con.cursor()

        # filling table with precious data
        for key, value in data.items():
            params = [key, value]
            cur.execute("""INSERT INTO bridge (title, full_title) VALUES (?, ?)""", params)


def fill_the_day_table_for_a_month(data):
    with sq.connect('bridges_database.db') as con:
        cur = con.cursor()

        year = datetime.now().year
        month = datetime.now().month
        days_number = (date(year, month + 1, 1) - date(year, month, 1)).days

        cur.execute("""DELETE FROM day""")

        for day in range(1, days_number):

            if day < 10:
                params = [f'0{day}.0{month}.{year}']
            else:
                params = [f'{day}.0{month}.{year}']

            cur.execute("""INSERT INTO day (ts) VALUES (?)""", params)


def get_list_of_the_bridges():
    with sq.connect('bridges_database.db') as con:
        cur = con.cursor()

        cur.execute("""SELECT full_title FROM bridge LEFT JOIN day ON """)
