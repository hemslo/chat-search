from typing import Annotated

from fastapi import Depends

from app.dependencies.redis import RedisDep
from app.dependencies.text_splitter import TextSplitterDep
from app.models.web_document import WebDocument

DIGEST_PREFIX = "digest"


class Repository:
    def __init__(self, redis: RedisDep, text_splitter: TextSplitterDep):
        self.redis = redis
        self.text_splitter = text_splitter

    def get_digest(self, source_id: str) -> str | None:
        digest = self.redis.client.get(f"{DIGEST_PREFIX}:{source_id}")
        return digest.decode() if digest else None

    def save(self, doc: WebDocument) -> None:
        docs = self.text_splitter.split_documents([doc])
        existing_keys = self.redis.client.keys(
            f"{self.redis.key_prefix}:{doc.source_id}:*"
        )
        if len(existing_keys) > len(docs):
            self.redis.client.delete(*existing_keys)
        self.redis.client.set(
            f"{DIGEST_PREFIX}:{doc.source_id}",
            doc.page_content_digest,
        )
        self.redis.add_documents(
            docs,
            ids=[f"{doc.source_id}:{idx}" for idx in range(len(docs))],
        )


RepositoryDep = Annotated[Repository, Depends(Repository)]
