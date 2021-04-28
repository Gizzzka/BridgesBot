import sqlite3 as sq
from datetime import date, time
from dateutil import parser


def convert_time(str_time):
    final = parser.parse(str_time)
    time_obj = (time(final.hour, final.minute))
    return time_obj


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
                       opened_at TEXT NOT NULL,
                       closed_at TEXT NOT NULL,
                       bridge_id INTEGER NOT NULL,
                       date_id INTEGER NOT NULL,
                       FOREIGN KEY (bridge_id) REFERENCES bridges_titles (id),
                       FOREIGN KEY (date_id) REFERENCES date (id)
                    )""")


def init_titles(titles):
    with sq.connect('Bridges_database.db', detect_types=sq.PARSE_DECLTYPES) as con:
        cur = con.cursor()

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

            lst = [bridge]
            cur.execute("""SELECT id FROM bridges_titles WHERE ? == full_title""", lst)
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

        cur.execute("""SELECT date.date, bridges_titles.full_title, opened_at, closed_at from opening_time
                       JOIN bridges_titles 
                       ON bridges_titles.id == bridge_id
                       JOIN date
                       ON date.id = date_id
                    """)
        result = cur.fetchall()

        data_dict = {}
        for elem in result:

            if elem[1] not in data_dict.keys():
                data_dict[elem[1]] = [{convert_time(elem[2]): convert_time(elem[3])}]
            elif elem[1] in data_dict.keys():
                data_dict[elem[1]][0][convert_time(elem[2])] = convert_time(elem[3])

        print('***Data were successfully retrieved***')
        print(data_dict)

        return data_dict


def create_db(data_dict):
    init_db()
    print('***The database was created successfully***')

    init_titles({'МАН': 'Мост Александра Невского', 'БЖМ': 'Биржевой мост', 'БВМ': 'Благовещенский мост',
                 'БОМ': 'Большеохтинский мост', 'ВДМ': 'Володарский мост', 'ДЦМ': 'Дворцовый мост',
                 'ЛТМ': 'Литейный мост', 'ТРМ': 'Троицкий мост', 'ТУ': 'Тучков мост'})
    init_date()
    print('***The date table and the titles table were created successfully***')

    init_opening_time(data_dict)
    print('***The opening_time table was created successfully***\n***Now you can use the get_data() function***')
