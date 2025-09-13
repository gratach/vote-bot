from sqlite3 import Connection, Cursor
import json
import time


class SQLiteActionLogger:
    """
    This class logs actions (JSON-serializable dictionaries) into a SQLite database.
    Each action is stored with a timestamp in unix epoch format.
    """
    def __init__(self, sqliteFilePath):
        self.conn = Connection(sqliteFilePath)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                action TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def logAction(self, actionDict, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        actionJson = json.dumps(actionDict)
        self.cursor.execute("""
            INSERT INTO actions (timestamp, action) VALUES (?, ?)
        """, (timestamp, actionJson))
        self.conn.commit()

    def iterateActions(self):
        self.cursor.execute("SELECT timestamp, action FROM actions ORDER BY id ASC")
        for row in self.cursor.fetchall():
            timestamp, actionJson = row
            actionDict = json.loads(actionJson)
            yield (timestamp, actionDict)