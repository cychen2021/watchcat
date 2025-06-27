from phdkit.util import todo
from phdkit.configlib import configurable, setting
from abc import ABC, abstractmethod
from phdkit.util import unimplemented


def __read_config(config_file: str | None = None):
    return todo()


def __read_env(config_file: str | None = None):
    return todo()


@configurable(__read_config, config_key="datastore", load_env=__read_env)
class Database(ABC):
    @setting("path")
    def db_path(self) -> str: ...

    def __init__(self, init_script: str):
        self._init_script = init_script

    @abstractmethod
    def open(self):
        unimplemented()

    @abstractmethod
    def close(self):
        unimplemented()
