import json
from pathlib import Path
from typing import Optional

import numpy as np
import psycopg2
from embedding_storage.storage import EmbeddingStorage, SearchResult


def main():
    with open(Path(__file__).absolute().parent / '..' / 'dev-config.json', 'r') as f:
        CONFIG = json.load(f)
    pg_config = CONFIG["pg"]

    storage = PostgresEmbeddingStorage.from_config('test', pg_config)
    storage.initialize()
    storage.save_embedding('test', b'123' * 512, '1')


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
                        text TEXT NOT NULL PRIMARY KEY,
                        embedding vector(1536) NOT NULL,
                        version TEXT NOT NULL
                    );
                """)

    def text_to_version(self, text: str) -> Optional[str]:
        with self._pg:
            with self._pg.cursor() as c:
                c.execute(f"""
                    SELECT version FROM {self._namespace}_texts
                    WHERE text = %s
                    LIMIT 1;
                """, (text,))

                row = c.fetchone()
                if row:
                    return row[0]

        return None

    def save_embedding(self, text: str, embedding: np.array, version: str) -> None:
        with self._pg:
            with self._pg.cursor() as c:
                c.execute(f"""
                    INSERT INTO {self._namespace}_texts (text, embedding, version)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (text) DO UPDATE
                        SET embedding = EXCLUDED.embedding, version = EXCLUDED.version;
                    """,
                    (text, list(embedding), version)
                )

    def knn(self, embedding: bytes, *, k: int = 100, version: str) -> SearchResult:
        return SearchResult(texts=[])


if __name__ == '__main__':
    main()
