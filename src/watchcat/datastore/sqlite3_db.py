import sqlite3
from .database import Database

class SQLite3DB(Database):
    def __init__(self, init_script: str):
        super().__init__(init_script)
        self.connection: sqlite3.Connection
        self.cursor: sqlite3.Cursor

    def open(self):
        self.connection = sqlite3.connect(self.init_script)
        self.cursor = self.connection.cursor()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
