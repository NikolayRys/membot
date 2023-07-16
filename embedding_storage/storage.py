from dataclasses import dataclass
from typing import Protocol, List, Optional

import numpy as np


@dataclass
class SearchResult:
    texts: List[str]


class EmbeddingStorage(Protocol):
    def initialize(self) -> None:
        ...

    def text_to_version(self, text: str) -> Optional[str]:
        ...

    def save_embedding(self, text: str, embedding: np.array, version: str) -> None:
        ...

    def knn(self, embedding: bytes, *, k: int = 100, version: str) -> SearchResult:
        ...
