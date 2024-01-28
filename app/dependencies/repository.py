from typing import Annotated

from fastapi import Depends

from app.dependencies.redis import RedisDep
from app.models.web_document import WebDocument, DOC_FIELDS


class Repository:
    def __init__(self, redis: RedisDep):
        self.redis = redis

    def get(self, source_id: str) -> WebDocument | None:
        values = self.redis.client.hmget(
            f"{self.redis.key_prefix}:{source_id}", DOC_FIELDS
        )
        if all(v is None for v in values):
            return None
        return WebDocument(
            metadata=dict(zip(DOC_FIELDS[:-1], values[:-1])),
            page_content=values[-1],
        )

    def save(self, doc: WebDocument) -> None:
        self.redis.add_documents([doc], ids=[doc.source_id()])


RepositoryDep = Annotated[Repository, Depends(Repository)]
