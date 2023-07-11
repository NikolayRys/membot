from dataclasses import dataclass
from typing import Protocol, List, Optional


@dataclass
class SearchResult:
    texts: List[str]


class EmbeddingStorage(Protocol):
    def initialize(self) -> None:
        ...

    def text_to_version(self, text: str) -> Optional[str]:
        ...

    def save_embedding(self, text: str, embedding: bytes, version: str) -> None:
        ...

    def knn(self, embedding: bytes, *, k: int = 100, version: str) -> SearchResult:
        ...
