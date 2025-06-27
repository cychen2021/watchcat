from abc import ABC, abstractmethod
from phdkit.util import unimplemented

class Database(ABC):
    def __init__(self, init_script: str):
        self.init_script = init_script

    @abstractmethod
    def open(self):
        unimplemented()

    @abstractmethod
    def close(self):
        unimplemented()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
