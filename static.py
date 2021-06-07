DB_PATH = 'bridges_database.db'
#
#
CREATE_TITLES = """CREATE TABLE IF NOT EXISTS bridges_titles (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           short_title TEXT,
                           full_title TEXT
                        )"""

INSERT_TITLES = """INSERT INTO bridges_titles(short_title, full_title) VALUES (?, ?)"""
SELECT_TITLES_ID = """SELECT id FROM bridges_titles WHERE ? == full_title"""
DROP_TITLES = """DROP TABLE IF EXISTS bridges_titles"""
#
#
INSERT_DATE = """INSERT INTO date (date) VALUES(?)"""
CREATE_DATE = """CREATE TABLE IF NOT EXISTS date (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           date DATE
                        )"""
SELECT_DATE_ID = """SELECT id FROM date WHERE ? == date"""
DROP_DATE = """DROP TABLE IF EXISTS date"""
#
#
INSERT_OPENINGS = """INSERT INTO opening_time(closed_at, opened_at, bridge_id, date_id)
                                       VALUES (?, ?, ?, ?)"""
CREATE_OPENINGS = """CREATE TABLE IF NOT EXISTS opening_time (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           opened_at TEXT NOT NULL,
                           closed_at TEXT NOT NULL,
                           bridge_id INTEGER NOT NULL,
                           date_id INTEGER NOT NULL,
                           FOREIGN KEY (bridge_id) REFERENCES bridges_titles (id),
                           FOREIGN KEY (date_id) REFERENCES date (id)
                        )"""
DROP_OPENINGS = """DROP TABLE IF EXISTS opening_time"""
#
#
GET_BY_DATE = """SELECT bridges_titles.full_title, opened_at, closed_at FROM opening_time
                                   JOIN bridges_titles
                                   ON bridges_titles.id == bridge_id
                                   JOIN date
                                   ON date_id == ?
                                """
GET_BY_DATE_ALT = """SELECT date.date, bridges_titles.full_title, opened_at, closed_at FROM opening_time
                                   JOIN bridges_titles
                                   ON bridges_titles.id == bridge_id
                                   JOIN date
                                   ON date_id == ?
                                """

GET_BY_TITLE = """SELECT opened_at, closed_at FROM opening_time WHERE bridge_id == ? AND date_id == ?"""

GET_BY_TITLE_ALT = """SELECT date.date, bridges_titles.full_title, 
                                (SELECT opened_at FROM opening_time WHERE bridge_id == ?), 
                                (SELECT closed_at FROM opening_time WHERE bridge_id == ?) 
                           FROM opening_time 
                           JOIN bridges_titles ON bridges_titles.id == ? 
                           JOIN date ON date_id == ?"""