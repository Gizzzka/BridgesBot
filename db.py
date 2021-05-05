from datetime import date, time
from parser import get_schedule
from dateutil import parser
from pprint import pprint
import sqlite3 as sq
import envs


def convert_time(str_time):
    final = parser.parse(str_time)
    time_obj = (time(final.hour, final.minute))
    return time_obj


def init_db():
    with sq.connect(envs.DB_PATH, detect_types=sq.PARSE_DECLTYPES) as con:
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
                       opened_at TEXT NOT NULL,
                       closed_at TEXT NOT NULL,
                       bridge_id INTEGER NOT NULL,
                       date_id INTEGER NOT NULL,
                       FOREIGN KEY (bridge_id) REFERENCES bridges_titles (id),
                       FOREIGN KEY (date_id) REFERENCES date (id)
                    )""")


def init_titles(titles):
    with sq.connect(envs.DB_PATH, detect_types=sq.PARSE_DECLTYPES) as con:
        cur = con.cursor()

        for short_title, full_title in titles.items():
            cur.execute("""INSERT INTO bridges_titles(short_title, full_title) VALUES (?, ?)""",
                        (short_title, full_title))


def init_date(dell=False):
    with sq.connect(envs.DB_PATH, detect_types=sq.PARSE_DECLTYPES) as con:
        cur = con.cursor()

        if dell:
            cur.execute("""DELETE FROM date""")

        today_date = [date.isoformat(date.today())]
        cur.execute("""INSERT INTO date (date) VALUES(?)""", today_date)


def init_opening_time(bridges_dictt, dell=False):
    with sq.connect(envs.DB_PATH, detect_types=sq.PARSE_DECLTYPES) as con:
        cur = con.cursor()

        if dell:  # delete old opening time
            cur.execute("""DELETE FROM opening_time""")

        for bridge in bridges_dictt:
            cur.execute("""SELECT id FROM bridges_titles WHERE ? == full_title""", [bridge])
            bridge_id = cur.fetchall()
            bridge_id = bridge_id[0][0]

            cur.execute("""SELECT id FROM date WHERE ? == date""", [date.isoformat(date.today())])
            date_id = cur.fetchall()
            date_id = date_id[0][0]

            for embedded_dict in bridges_dictt[bridge]:
                for opened_at, closed_at in embedded_dict.items():
                    cur.execute("""INSERT INTO opening_time(closed_at, opened_at, bridge_id, date_id)
                                   VALUES (?, ?, ?, ?)""",
                                [time.isoformat(closed_at), time.isoformat(opened_at), bridge_id, date_id]
                                )


def create_db():
    init_db()
    print('***The database was created successfully***')

    init_titles({'АЛЕ': 'Мост Александра Невского', 'БИР': 'Биржевой мост', 'БЛА': 'Благовещенский мост',
                 'БОЛ': 'Большеохтинский мост', 'ВОЛ': 'Володарский мост', 'ДВО': 'Дворцовый мост',
                 'ЛИТ': 'Литейный мост', 'ТРО': 'Троицкий мост', 'ТУЧ': 'Тучков мост'})
    print('***The titles were added successfully***\n***The database was created successfully***')


def fill_data(data_dict, dell=False):  # if dell == True, all previous data in the db will be deleted
    init_date(dell)
    print("***Today's date was added***")

    init_opening_time(data_dict, dell)
    print('***The opening time periods were added***\n***Now you can use the get_data_by_date() function***')


def get_data_by_date(current_date=date.today()):
    current_date = date.isoformat(current_date)

    with sq.connect(envs.DB_PATH, detect_types=sq.PARSE_DECLTYPES) as con:
        cur = con.cursor()

        cur.execute("""SELECT id FROM date
                               WHERE date == ?
                            """, [current_date])
        date_id = [cur.fetchall()[0][0]]

        cur.execute("""SELECT date.date, bridges_titles.full_title, opened_at, closed_at from opening_time
                               JOIN bridges_titles
                               ON bridges_titles.id == bridge_id
                               JOIN date
                               ON date_id == ?
                            """, date_id)
        result = cur.fetchall()

        data_dict = {}
        for elem in result:

            if elem[1] not in data_dict.keys():
                data_dict[elem[1]] = [{convert_time(elem[2]): convert_time(elem[3])}]
            elif elem[1] in data_dict.keys():
                data_dict[elem[1]][0][convert_time(elem[2])] = convert_time(elem[3])

        print('***Data were successfully retrieved***')
        pprint(data_dict)

        return data_dict

