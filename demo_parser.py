from time import sleep
import random
import json
import sqlite3 as sq
from selenium import webdriver
from pprint import pprint
from datetime import datetime, date, time
import envs


class BridgesDict:
    def __init__(self):
        self.bridge_dict = {}
        fo = webdriver.FirefoxOptions()

        fo.add_argument('--headless')  # enable silent mode

        fp = webdriver.FirefoxProfile()  # disable images load
        fp.set_preference('permissions.default.image', 2)
        fp.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        fp.update_preferences()

        self.path = 'C:/Users/iljus/Desktop/Actual code/Trying selenium/geckodriver.exe'
        self.alt_path = '/Users/abarnett/Documents/geckodriver'

        self.driver = webdriver.Firefox(executable_path=self.alt_path,
                                        firefox_profile=fp,
                                        options=fo)
        self.url = 'https://mostotrest-spb.ru/'

    @staticmethod
    def fix_title(title):
        # fixing two-words titles
        if len(title.split(' ')) >= 2:
            # defining final variable
            fixed_title = ''

            # making all letters after the first lowercase
            for word in title.split(' '):
                fixed_title += word[0]
                fixed_title += word[1:].lower()
                fixed_title += ' '

            # get rid of the last space
            fixed_title = 'Мост ' + fixed_title[:-1]

        # fixing one-word titles
        else:
            fixed_title = title[0]
            fixed_title += title[1:].lower()

            fixed_title = fixed_title + ' мост'

        return fixed_title

    @staticmethod
    def fix_time(raw):
        try:
            return datetime.strptime(raw, '%H:%M').time()
        except Exception as ex:
            # print(ex)
            return datetime.strptime(raw, '%H:%M:%S').time()

    @staticmethod
    def fix_schedule(wrong_schedule):
        result = {}

        # fixing schedules with small time intervals
        if len(wrong_schedule) > 2:
            # adding bridge opening time
            result[BridgesDict.fix_time(wrong_schedule[-2])] = BridgesDict.fix_time(wrong_schedule[0])

            # adding small time intervals
            if len(wrong_schedule) > 4:
                result[BridgesDict.fix_time(wrong_schedule[2])] = BridgesDict.fix_time(wrong_schedule[3])

            # adding bridge closing time
            result[BridgesDict.fix_time(wrong_schedule[-3])] = BridgesDict.fix_time(wrong_schedule[-1])

        elif len(wrong_schedule) == 2:
            result[BridgesDict.fix_time(wrong_schedule[0])] = BridgesDict.fix_time(wrong_schedule[1])

        # if argument is too short
        else:
            result = {}

        return [result]

    def get_schedule(self):
        bridge_dict = {}
        try:
            self.driver.get(self.url)
            sleep(2)
            self.driver.find_element_by_xpath(
                '/html/body/div[1]/div/div[1]/div[3]'
            ).click()  # selecting full schedule
            sleep(2)
            # finding tag <div> with all bridges tags
            bridges_divs = self.driver.find_elements_by_class_name('bridge')
            # iterating throw each bridge tag and filling the dict
            for bridge in bridges_divs:
                bridge_name = bridge.find_element_by_class_name('name').text
                bridge_name = BridgesDict.fix_title(bridge_name)
                bridge_time = []
                for half_time_p in bridge.find_elements_by_tag_name('span'):
                    bridge_time.append(half_time_p.text)
                bridge_time = BridgesDict.fix_schedule(bridge_time)  # fixing the bridge time
                bridge_dict[bridge_name] = bridge_time  # filling the dict
        except Exception as ex:
            print(ex)

        self.driver.close()
        self.driver.quit()
        self.bridge_dict = bridge_dict

        return bridge_dict


# test = BridgesDict()
# test.get_schedule()


class Database:
    def __init__(self):
        self.db_name = 'Bridges_database.db'
        self.arg = sq.PARSE_DECLTYPES
        self.titles = {'АЛЕ': 'Мост Александра Невского', 'БИР': 'Биржевой мост', 'БЛА': 'Благовещенский мост',
                       'БОЛ': 'Большеохтинский мост', 'ВОЛ': 'Володарский мост', 'ДВО': 'Дворцовый мост',
                       'ЛИТ': 'Литейный мост', 'ТРО': 'Троицкий мост', 'ТУЧ': 'Тучков мост'}

    def init_db(self):
        with sq.connect(self.db_name, detect_types=self.arg) as con:
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

    def init_titles(self):
        with sq.connect(self.db_name, detect_types=self.arg) as con:
            cur = con.cursor()

            for short_title, full_title in self.titles.items():
                cur.execute("""INSERT INTO bridges_titles(short_title, full_title) VALUES (?, ?)""",
                            (short_title, full_title))

    def init_date(self, dell=False):
        with sq.connect(self.db_name, detect_types=self.arg) as con:
            cur = con.cursor()

            if dell:
                cur.execute("""DELETE FROM date""")

            today_date = [date.isoformat(date.today())]
            cur.execute("""INSERT INTO date (date) VALUES(?)""", today_date)

    def init_opening_time(self, dell=False):
        self.bridges_obj = BridgesDict()
        self.schedule = self.bridges_obj.get_schedule()

        with sq.connect(self.db_name, detect_types=self.arg) as con:
            cur = con.cursor()

            if dell:  # delete old opening time
                cur.execute("""DELETE FROM opening_time""")

            for bridge in self.schedule:
                cur.execute("""SELECT id FROM bridges_titles WHERE ? == full_title""", [bridge])
                bridge_id = cur.fetchall()
                bridge_id = bridge_id[0][0]

                cur.execute("""SELECT id FROM date WHERE ? == date""", [date.isoformat(date.today())])
                date_id = cur.fetchall()
                date_id = date_id[0][0]

                for embedded_dict in self.schedule[bridge]:
                    for opened_at, closed_at in embedded_dict.items():
                        cur.execute("""INSERT INTO opening_time(closed_at, opened_at, bridge_id, date_id)
                                       VALUES (?, ?, ?, ?)""",
                                    [time.isoformat(closed_at), time.isoformat(opened_at), bridge_id, date_id]
                                    )

    def create_db(self):
        Database.init_db(self)
        print('***The database was created successfully***')

        Database.init_titles(self)
        print('***The titles were added successfully***\n***The database was created successfully***')

    def fill_data(self, dell=False):  # if dell == True, all previous data in the db will be deleted
        Database.init_date(self)
        print("***Today's date was added***")

        Database.init_opening_time(self, dell=False)
        print('***The opening time periods were added***\n***Now you can use the get_data_by_date() function***')

    def get_data_by_date(self, current_date=date.today()):
        current_date = date.isoformat(current_date)

        with sq.connect(self.db_name, detect_types=self.arg) as con:
            cur = con.cursor()

            cur.execute("""SELECT id FROM date WHERE date == ?""", [current_date])
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
                    data_dict[elem[1]] = [{BridgesDict.fix_time(elem[2]): BridgesDict.fix_time(elem[3])}]
                elif elem[1] in data_dict.keys():
                    data_dict[elem[1]][0][BridgesDict.fix_time(elem[2])] = BridgesDict.fix_time(elem[3])

            print('***Data were successfully retrieved***')
            pprint(data_dict)

            return data_dict

    def get_data_by_title(self, title):
        with sq.connect(self.db_name, detect_types=self.arg) as con:
            cur = con.cursor()

            current_date = date.isoformat(date.today())
            cur.execute("""SELECT id FROM date WHERE date == ?""", [current_date])
            date_id = cur.fetchall()[0][0]

            cur.execute("""SELECT id FROM bridges_titles WHERE full_title == ?""", [title])
            title_id = cur.fetchall()[0][0]

            cur.execute("""SELECT date.date, bridges_titles.full_title, 
                                (SELECT opened_at FROM opening_time WHERE bridge_id = ?), 
                                (SELECT closed_at FROM opening_time WHERE bridge_id = ?) 
                           FROM opening_time 
                           JOIN bridges_titles 
                           ON bridges_titles.id == ? 
                           JOIN date ON date_id == ?""", [title_id, title_id, title_id, date_id])
            result = cur.fetchall()

            data_dict = {}
            for elem in result:

                if elem[1] not in data_dict.keys():
                    data_dict[elem[1]] = [{BridgesDict.fix_time(elem[2]): BridgesDict.fix_time(elem[3])}]
                elif elem[1] in data_dict.keys():
                    data_dict[elem[1]][0][BridgesDict.fix_time(elem[2])] = BridgesDict.fix_time(elem[3])

            print('***Data were successfully retrieved***')
            pprint(data_dict)

            return data_dict

    def get_data_by_short_title(self, short_title):
        with sq.connect(self.db_name, detect_types=self.arg) as con:
            cur = con.cursor()

            current_date = date.isoformat(date.today())
            cur.execute("""SELECT id FROM date WHERE date == ?""", [current_date])
            date_id = cur.fetchall()[0][0]

            cur.execute("""SELECT id FROM bridges_titles WHERE short_title == ?""", [short_title])
            title_id = cur.fetchall()[0][0]

            cur.execute("""SELECT date.date, bridges_titles.full_title, 
                                (SELECT opened_at FROM opening_time WHERE bridge_id = ?), 
                                (SELECT closed_at FROM opening_time WHERE bridge_id = ?) 
                           FROM opening_time 
                           JOIN bridges_titles 
                           ON bridges_titles.id == ? 
                           JOIN date ON date_id == ?""", [title_id, title_id, title_id, date_id])
            result = cur.fetchall()

            data_dict = {}
            for elem in result:

                if elem[1] not in data_dict.keys():
                    data_dict[elem[1]] = [{BridgesDict.fix_time(elem[2]): BridgesDict.fix_time(elem[3])}]
                elif elem[1] in data_dict.keys():
                    data_dict[elem[1]][0][BridgesDict.fix_time(elem[2])] = BridgesDict.fix_time(elem[3])

            print('***Data were successfully retrieved***')
            pprint(data_dict)

            return data_dict


def main():
    test = Database()
    print('***A Database object was created***')
    test.get_data_by_date()
    test.get_data_by_title('Мост Александра Невского')
    test.get_data_by_short_title('АЛЕ')


if __name__ == '__main__':
    main()
