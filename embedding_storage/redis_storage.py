from typing import Optional

import numpy as np
from redis.client import Redis
from redis.commands.search.field import VectorField, TextField
from redis.commands.search.query import Query
from redis.exceptions import ResponseError

from embedding_storage.storage import EmbeddingStorage, SearchResult


class RedisEmbeddingStorage(EmbeddingStorage):
    def __init__(self, namespace: str, redis: Redis) -> None:
        self._redis = redis
        self._namespace = namespace

    def initialize(self) -> None:
        try:
            self._redis.ft(self._namespace).dropindex()
        except ResponseError:
            pass

        emb_field = VectorField(
            name='embedding',
            algorithm='HNSW',
            attributes=dict(
                type='FLOAT64',
                dim=1536,
                distance_metric='COSINE',
            ),
        )
        version_field = TextField('version')

        self._redis.ft(self._namespace).create_index([
            emb_field,
            version_field,
        ])

    def text_to_version(self, text: str) -> Optional[str]:
        return self._redis.hget(f'text:{text}', 'version')

    def save_embedding(self, text: str, embedding: np.array, version: str) -> None:
        self._redis.hset(f"text:{text}", mapping=dict(
            embedding=embedding.tobytes(),
            text=text,
            version=version,
        ))

    def knn(self, embedding: bytes, *, k: int = 100, version: str) -> SearchResult:
        q = (
            Query(f"(@version:{version})=>[KNN {k} @embedding $e]")
            .return_field('text')
            .return_field('__embedding_score')
            .dialect(2)
        )
        result = self._redis.ft(self._namespace).search(q, query_params={"e": embedding})

        return SearchResult(texts=[d.text for d in result.docs])
