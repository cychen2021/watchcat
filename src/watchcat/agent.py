import tomllib
from abc import ABC
from dataclasses import dataclass
from phdkit.configlib import configurable, setting, ConfigReader

def __read_config(config_file: str | None = None):
    with open(config_file if config_file is not None else "config.toml", "rb") as f:
        return tomllib.load(f)

class ProviderInfo(ABC):
    pass

@dataclass
class GeminiProviderInfo(ProviderInfo):
    api_key: str

@configurable(__read_config)
class Agent:
    @property
    def model(self):
        return self.__model

    @model.setter
    @setting("model")
    def model(self, model):
        self.__model = model

    @property
    def gemini_api_key(self):
        if self.__provider_info is None:
            return None
        if "gemini" not in self.__provider_info:
            return None
        return self.__provider_info["gemini"].api_key

    @gemini_api_key.setter
    @setting("provider.gemini.api_key")
    def gemini_api_key(self, gemini_api_key):
        if self.__provider_info is None:
            self.__provider_info = {}
        if "gemini" not in self.__provider_info:
            self.__provider_info["gemini"] = GeminiProviderInfo(api_key=gemini_api_key)
        else:
            self.__provider_info["gemini"].api_key = gemini_api_key

    def __init__(self):
        self.__model = None
        self.__provider_info = None