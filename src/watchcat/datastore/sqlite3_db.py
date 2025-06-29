import sqlite3
import sqlite_vec
from phdkit.configlib import configurable, setting
from phdkit.util import todo
from .database import Database


def __read_config(config_file: str | None = None):
    return todo()


def __read_env(config_file: str | None = None):
    return todo()


@configurable(__read_config, config_key="store.sqlite3", load_env=__read_env)
class SQLite3DB(Database):
    @setting.getter("init_script")
    def init_script(self) -> str:
        return self._init_script

    @init_script.setter
    def _set_init_script(self, value: str):
        self._init_script = value

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
