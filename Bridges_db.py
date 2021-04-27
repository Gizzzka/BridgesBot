import sqlite3 as sq
from datetime import date, time


def init_db():
    with sq.connect('Bridges_database.db', detect_types=sq.PARSE_DECLTYPES) as con:
        cur = con.cursor()

        cur.execute("""DROP TABLE IF EXISTS bridges_titles""")
        cur.execute("""DROP TABLE IF EXISTS date""")
        cur.execute("""DROP TABLE IF EXISTS opening_time""")

        cur.execute("""CREATE TABLE IF NOT EXISTS bridges_titles (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       short_title TEXT,
                       full_title TEXT
                    )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS date (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       date DATE
                    )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS opening_time (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       opened_at TIMESTAMP NOT NULL,
                       closed_at TIMESTAMP NOT NULL,
                       bridge_id INTEGER NOT NULL,
                       date_id INTEGER NOT NULL,
                       FOREIGN KEY (bridge_id) REFERENCES bridges_titles (id),
                       FOREIGN KEY (date_id) REFERENCES date (id)
                    )""")


def init_titles(titles):
    with sq.connect('Bridges_database.db', detect_types=sq.PARSE_DECLTYPES) as con:
        cur = con.cursor()

        # cur.execute("""DELETE FROM bridges_titles""")

        i = 1
        for short_title, full_title in titles.items():
            cur.execute("""INSERT INTO bridges_titles(id, short_title, full_title) VALUES (?, ?, ?)""",
                        (i, short_title, full_title))
            i += 1


def init_date():
    with sq.connect('Bridges_database.db', detect_types=sq.PARSE_DECLTYPES) as con:
        cur = con.cursor()

        cur.execute("""DELETE FROM date""")

        date_id = 1
        today_date = date.isoformat(date.today())

        cur.execute("""INSERT INTO date(id, date) VALUES(?, ?)""", (date_id, today_date))


def init_opening_time(bridges_dictt):
    with sq.connect('Bridges_database.db', detect_types=sq.PARSE_DECLTYPES) as con:
        cur = con.cursor()

        cur.execute("""DELETE FROM opening_time""")

        elem_id = 1
        for bridge in bridges_dictt:

            cur.execute("""SELECT id FROM bridges_titles WHERE ? == full_title""", [bridge])
            bridge_id = cur.fetchall()
            bridge_id = bridge_id[0][0]

            cur.execute("""SELECT id FROM date WHERE ? == date""", [date.isoformat(date.today())])
            date_id = cur.fetchall()
            date_id = date_id[0][0]

            for embedded_dict in bridges_dict[bridge]:

                for opened_at, closed_at in embedded_dict.items():

                    cur.execute("""INSERT INTO opening_time(id, closed_at, opened_at, bridge_id, date_id)
                                   VALUES (?, ?, ?, ?, ?)""",
                                [elem_id, time.isoformat(closed_at), time.isoformat(opened_at), bridge_id, date_id]
                                )
                    elem_id += 1


bridges_dict = {'Мост Александра Невского': [{time(2, 20): time(4, 20), time(4, 40): time(5, 20)}],
                'Володарский мост': [{time(2, 20): time(3, 20)}],
                'Большеохтинский мост': [{time(2): time(5)}]
                }


def get_data():
    with sq.connect('Bridges_database.db', detect_types=sq.PARSE_DECLTYPES) as con:
        cur = con.cursor()

        cur.execute("""SELECT opened_at, closed_at from opening_time""")
        test = cur.fetchall()

        print(test)


get_data()
