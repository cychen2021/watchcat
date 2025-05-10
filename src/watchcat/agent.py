import tomllib
from abc import ABC
from dataclasses import dataclass
from phdkit.configlib import configurable, setting, ConfigReader


def __read_config(config_file: str | None = None):
    with open(config_file if config_file is not None else "config.toml", "rb") as f:
        config = tomllib.load(f)

    def check_keys(d: dict):
        for k, v in d.items():
            assert isinstance(k, str), f"Key {k} is not a string"
            if k.endswith("api_key"):
                raise ValueError(f"You should put API keys in the env.toml file")
            if isinstance(v, dict):
                check_keys(v)

    check_keys(config)
    return config


def __read_env_config(config_file: str | None = None):
    with open(config_file if config_file is not None else "env.toml", "rb") as f:
        return tomllib.load(f)


class ProviderInfo(ABC):
    pass


@dataclass
class GeminiProviderInfo(ProviderInfo):
    api_key: str


@dataclass
class ModelInfo:
    generation_model: str | None
    embedding_model: str | None


@configurable(__read_config, __read_env_config)
class Agent:
    @property
    def model(self):
        if self.__model is None:
            return None
        return self.__model.generation_model

    @model.setter
    @setting("model")
    def model(self, model):
        if self.__model is None:
            self.__model = ModelInfo(generation_model=model, embedding_model=None)
        else:
            self.__model.generation_model = model

    @property
    def embedding_model(self):
        if self.__model is None:
            return None
        return self.__model.embedding_model

    @embedding_model.setter
    @setting("embedding_model")
    def embedding_model(self, embedding_model):
        if self.__model is None:
            self.__model = ModelInfo(
                generation_model=None, embedding_model=embedding_model
            )
        else:
            self.__model.embedding_model = embedding_model

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
