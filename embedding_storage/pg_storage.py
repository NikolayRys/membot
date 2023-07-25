import hashlib
from typing import Optional

import numpy as np
import psycopg2
from embedding_storage.storage import EmbeddingStorage, SearchResult


class PostgresEmbeddingStorage(EmbeddingStorage):
    def __init__(self, namespace: str, pg: psycopg2.extensions.connection) -> None:
        self._pg = pg
        self._namespace = namespace

    @classmethod
    def from_config(cls, namespace: str, config: dict) -> 'PostgresEmbeddingStorage':
        conn = psycopg2.connect(
            host=config["host"],
            database=config["db"],
            user=config["user"],
            password=config["password"],
        )

        return cls(namespace, conn)

    def initialize(self) -> None:
        with self._pg:
            with self._pg.cursor() as c:
                c.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self._namespace}_texts (
                        text_md5 CHAR(32) NOT NULL PRIMARY KEY,
                        text TEXT NOT NULL,
                        embedding vector(1536) NOT NULL,
                        version TEXT NOT NULL
                    );
                """)

    def text_to_version(self, text: str) -> Optional[str]:
        text_md5: str = hashlib.md5(text.encode('utf-8')).hexdigest()
        with self._pg:
            with self._pg.cursor() as c:
                c.execute(f"""
                    SELECT version FROM {self._namespace}_texts
                    WHERE text_md5 = %s
                    LIMIT 1;
                """, (text_md5,))

                row = c.fetchone()
                if row:
                    return row[0]

        return None

    def save_embedding(self, text: str, embedding: np.ndarray, version: str) -> None:
        text_md5: str = hashlib.md5(text.encode('utf-8')).hexdigest()
        with self._pg:
            with self._pg.cursor() as c:
                c.execute(f"""
                    INSERT INTO {self._namespace}_texts (text_md5, text, embedding, version)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (text_md5) DO UPDATE
                        SET embedding = EXCLUDED.embedding, version = EXCLUDED.version;
                    """,
                    (text_md5, text, list(embedding), version)
                )

    def knn(self, embedding: np.ndarray,  *, k: int = 100, version: str) -> SearchResult:
        with self._pg:
            with self._pg.cursor() as c:
                c.execute(f"""
                    SELECT text
                    FROM {self._namespace}_texts
                    WHERE version = %s
                    ORDER BY (1 - (embedding <=> %s::vector)) DESC
                    LIMIT %s
                """, (version, list(embedding), k)
                )

                return SearchResult(texts=[row[0] for row in c.fetchall()])
