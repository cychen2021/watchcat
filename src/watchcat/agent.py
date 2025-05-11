import tomllib
from abc import ABC
from dataclasses import dataclass
from phdkit.configlib import configurable, setting
from phdkit.log import Logger, LogOutput, EmailNotifier
from typing import Sequence
from arxiv import (
    Client as ArxivClient,
    Search as ArxivSearch,
    SortCriterion as ArxivSortCriterion,
)
from datetime import datetime, UTC
from litellm import embedding
from .paper import ArxivPaper

logger = Logger(__file__, outputs=[LogOutput.stderr()])


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


def __read_env(config_file: str | None = None):
    with open(config_file if config_file is not None else "env.toml", "rb") as f:
        return tomllib.load(f)


@dataclass
class ProviderInfo:
    base_url: str | None


@dataclass
class GeminiProviderInfo(ProviderInfo):
    api_key: str | None


@dataclass
class ModelInfo:
    generation_model: str | None
    embedding_model: str | None


@configurable(__read_config, __read_env, config_key="agent")
class Agent:
    MAX_PAPERS_PER_DAY = 100

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
        embedding_model_updated = embedding_model != self.__model.embedding_model
        self.__model.embedding_model = embedding_model
        if embedding_model_updated:
            self.update_topic_embedding()

    @property
    def gemini_base_url(self):
        if "gemini" not in self.__provider_info:
            return None
        return self.__provider_info["gemini"].base_url

    @gemini_base_url.setter
    @setting("provider.gemini.base_url")
    def gemini_base_url(self, gemini_base_url):
        if "gemini" not in self.__provider_info:
            self.__provider_info["gemini"] = GeminiProviderInfo(base_url=gemini_base_url)  # type: ignore
        else:
            self.__provider_info["gemini"].base_url = gemini_base_url

    @property
    def gemini_api_key(self):
        if "gemini" not in self.__provider_info:
            return None
        return self.__provider_info["gemini"].api_key  # type: ignore

    @gemini_api_key.setter
    @setting("provider.gemini.api_key")
    def gemini_api_key(self, gemini_api_key):
        if "gemini" not in self.__provider_info:
            self.__provider_info["gemini"] = GeminiProviderInfo(
                api_key=gemini_api_key, base_url=None
            )
        else:
            self.__provider_info["gemini"].api_key = gemini_api_key  # type: ignore

    @property
    def topic(self):
        return self.__topic

    @topic.setter
    @setting("topic")
    def topic(self, topic):
        topic_updated = topic != self.__topic
        self.__topic = topic
        if topic_updated:
            self.update_topic_embedding()

    @property
    def keywords(self):
        return self.__keywords

    @keywords.setter
    @setting("keywords")
    def keywords(self, keywords):
        self.__keywords = keywords

    @property
    def relevance_threshold(self):
        return self.__relevance_threshold

    @relevance_threshold.setter
    @setting("relevance_threshold")
    def relevance_threshold(self, relevance_threshold):
        self.__relevance_threshold = relevance_threshold

    def __init__(self):
        self.__model: ModelInfo = ModelInfo(generation_model=None, embedding_model=None)
        self.__provider_info: dict[str, ProviderInfo] = {}

        self.__topic: str | None = None
        self.__topic_embedding: list[float] | None = None
        self.__keywords: list[str] = []
        self.__arxiv_client: ArxivClient = ArxivClient()

        self.__relevance_threshold: float = 0.7

    def __get_embedding(self, text: str) -> list[float]:
        match self.embedding_model:
            case "gemini-embedding-exp-03-07":
                api_base = self.gemini_base_url
                api_key = self.gemini_api_key
        response = embedding(
            model=self.embedding_model,
            input=[text],
            api_base=api_base,
            api_key=api_key,
        )
        from litellm.types.utils import EmbeddingResponse

        assert isinstance(
            response, EmbeddingResponse
        ), f"Expected EmbeddingResponse, got {type(response)}"
        assert isinstance(
            response.data, list
        ), f"Expected list, got {type(response.data)}"
        if response.data:
            assert isinstance(
                response.data[0], float
            ), f"Expected float, got {type(response.data[0])}"
        return response.data

    def update_topic_embedding(self):
        if self.topic is None:
            raise ValueError("Topic is not set")
        if self.embedding_model is None:
            raise ValueError("Embedding model is not set")
        self.__topic_embedding = self.__get_embedding(self.topic)

    @staticmethod
    def compare_embeddings(embedding1: list[float], embedding2: list[float]) -> float:
        if len(embedding1) != len(embedding2):
            raise ValueError("Embeddings must be of the same length")
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        norm1 = sum(a**2 for a in embedding1) ** 0.5
        norm2 = sum(b**2 for b in embedding2) ** 0.5
        return dot_product / (norm1 * norm2) if norm1 and norm2 else 0.0

    def fetch_papers(self) -> Sequence[ArxivPaper]:
        now = datetime.now(UTC)
        today = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=UTC)
        yesterday = datetime(now.year, now.month, now.day - 1, 0, 0, 0, tzinfo=UTC)
        query = f"({"+OR+".join(self.__keywords)})+AND+submittedDate:[{yesterday.isoformat()}+TO+{today.isoformat()}]"
        search = ArxivSearch(
            query,
            sort_by=ArxivSortCriterion.Relevance,
            max_results=Agent.MAX_PAPERS_PER_DAY,
        )
        results = self.__arxiv_client.results(search)
        papers = []
        for result in results:
            paper = ArxivPaper(
                id=result.entry_id,
                title=result.title,
                authors=[author.name for author in result.authors],
                summary=result.summary,
                url=result.entry_id,
            )
            papers.append(paper)
        return papers

    def worth_reading(self, paper: ArxivPaper) -> bool:
        logger.info("Checking worthiness of paper", f"Paper {paper.id} ({paper.title})")
        topic_embedding = self.__topic_embedding
        if topic_embedding is None:
            raise ValueError("Topic embedding is not set")
        paper_embedding = self.get_paper_embedding(paper)
        relevance = self.compare_embeddings(topic_embedding, paper_embedding)
        worth = relevance >= self.__relevance_threshold

        if worth:
            logger.info(
                "Worth reading paper",
                f"Paper {paper.id} is worth reading (relevance: {relevance})",
            )

        return worth

    def get_paper_embedding(self, paper: ArxivPaper) -> list[float]:
        if self.embedding_model is None:
            raise ValueError("Embedding model is not set")
        return self.__get_embedding(paper.summary)
