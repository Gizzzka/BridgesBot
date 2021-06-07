import sqlite3 as sq
import Static
from Parser import Parser
from pprint import pprint
from datetime import date, time
from timeit import timeit


class Database:
    def __init__(self):
        self.db_name = static.DB_PATH
        self.arg = sq.PARSE_DECLTYPES

    def init_db(self):
        with sq.connect(self.db_name, detect_types=self.arg) as con:
            cur = con.cursor()

            cur.execute(static.DROP_TITLES)
            cur.execute(static.DROP_DATE)
            cur.execute(static.DROP_OPENINGS)

            cur.execute(static.CREATE_TITLES)
            cur.execute(static.CREATE_DATE)
            cur.execute(static.CREATE_OPENINGS)


class Titles(Database):
    def __init__(self):
        super().__init__()
        self.titles = {'АЛЕ': 'Мост Александра Невского', 'БИР': 'Биржевой мост', 'БЛА': 'Благовещенский мост',
                       'БОЛ': 'Большеохтинский мост', 'ВОЛ': 'Володарский мост', 'ДВО': 'Дворцовый мост',
                       'ЛИТ': 'Литейный мост', 'ТРО': 'Троицкий мост', 'ТУЧ': 'Тучков мост'}

    def init_titles(self):
        with sq.connect(self.db_name, detect_types=self.arg) as con:
            cur = con.cursor()
            for short_title, full_title in self.titles.items():
                cur.execute(static.INSERT_TITLES, (short_title, full_title))


class Date(Database):
    def __init__(self):
        super().__init__()
        self.date = date.isoformat(date.today())

    def init_date(self):
        with sq.connect(self.db_name, detect_types=self.arg) as con:
            cur = con.cursor()

            cur.execute(static.INSERT_DATE, [self.date])


class Openings(Database):
    def __init__(self):
        super().__init__()

    def init_opening_time(self):
        bridges_obj = Parser()
        bridges_obj.get_schedule()
        schedule = bridges_obj.bridge_dict

        with sq.connect(self.db_name, detect_types=self.arg) as con:
            cur = con.cursor()

            for bridge in schedule:
                cur.execute(static.SELECT_TITLES_ID, [bridge])
                bridge_id = cur.fetchall()
                bridge_id = bridge_id[0][0]

                cur.execute(static.SELECT_DATE_ID, [date.isoformat(date.today())])
                date_id = cur.fetchall()
                date_id = date_id[0][0]

                for opened_at in schedule[bridge]:
                    cur.execute(static.INSERT_OPENINGS,
                                [time.isoformat(schedule[bridge][opened_at]), time.isoformat(opened_at),
                                 bridge_id, date_id])


class Operator(Titles, Date, Openings):
    def __init__(self):
        super().__init__()

    def create_db(self):
        self.init_db()
        self.init_titles()

    def fill_data(self):
        self.init_date()
        self.init_opening_time()

    def get_data_by_date(self):
        current_date = date.isoformat(date.today())

        with sq.connect(self.db_name, detect_types=self.arg) as con:
            cur = con.cursor()

            cur.execute(static.SELECT_DATE_ID, [current_date])
            date_id = [cur.fetchall()[0][0]]

            cur.execute(static.GET_BY_DATE, date_id)
            result = cur.fetchall()

            data_dict = {}
            for elem in result:
                if elem[0] not in data_dict.keys():
                    data_dict[elem[0]] = {elem[1]: elem[2]}
                else:
                    data_dict[elem[0]].update({elem[1]: elem[2]})

            return data_dict

    def get_data_by_title(self, title):
        with sq.connect(self.db_name, detect_types=self.arg) as con:
            cur = con.cursor()

            current_date = date.isoformat(date.today())

            cur.execute(static.SELECT_TITLES_ID, [title])
            title_id = cur.fetchall()[0][0]

            cur.execute(static.SELECT_DATE_ID, [current_date])
            date_id = cur.fetchall()[0][0]

            cur.execute(static.GET_BY_TITLE, [title_id, date_id])
            result = cur.fetchall()

            data_dict = {title: {}}
            for elem in result:
                data_dict[title].update({elem[0]: elem[1]})

            return data_dict


def main():
    test = Operator()
    # test.create_db()
    # test.fill_data()
    pprint(test.get_data_by_date())
    print(test.get_data_by_title('Дворцовый мост'))


if __name__ == '__main__':
    print(timeit(main, number=1))
