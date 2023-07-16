from typing import List

import numpy as np
from langchain.embeddings import OpenAIEmbeddings

from embedding_storage.storage import EmbeddingStorage


class Embeddings:
    def __init__(
        self,
        *,
        storage: EmbeddingStorage,
        config: dict,
        version: str = '',
    ):
        self._config = config
        self._version = version

        self._open_ai_emb = OpenAIEmbeddings(
            openai_api_key=self._config['openai_api_key']
        )
        self._storage = storage

        self._storage.initialize()

    def _get_embedding(self, text: str) -> np.array:
        embedding = self._open_ai_emb.embed_query(text)

        return np.array(embedding)

    def _save_embedding(self, text: str, embedding: np.array) -> None:
        self._storage.save_embedding(
            text=text,
            embedding=embedding,
            version=self._version,
        )

    def add(self, text: str) -> np.array:
        found = self._storage.text_to_version(text)
        if found and found == self._version:
            return found

        embedding = self._get_embedding(text)
        self._save_embedding(text, embedding)

        return embedding.tobytes()

    def knn(self, text: str, *, k: int = 100) -> List[str]:
        emb: bytes = self._get_embedding(text).tobytes()

        return self._storage.knn(emb, k=k, version=self._version).texts
