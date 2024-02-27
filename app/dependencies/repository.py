from typing import Annotated

from fastapi import Depends

from app import config
from app.dependencies.html_preprocessor import preprocess
from app.dependencies.redis import RedisDep
from app.dependencies.text_splitter import TextSplitterDep
from app.models.document_model import DocumentModel
from app.models.html_document_request import HTMLDocumentRequest


class Repository:
    def __init__(self, redis: RedisDep, text_splitter: TextSplitterDep):
        self.redis = redis
        self.text_splitter = text_splitter

    def get_digest(self, source_id: str) -> str | None:
        digest = self.redis.client.get(f"{config.DIGEST_PREFIX}:{source_id}")
        return digest.decode() if digest else None

    def save(self, doc: HTMLDocumentRequest) -> None:
        docs = self.preprocess_doc(doc)
        existing_keys = self.redis.client.keys(
            f"{self.redis.key_prefix}:{doc.source_id}:*"
        )
        if len(existing_keys) > len(docs):
            self.redis.client.delete(*existing_keys)
        self.redis.add_documents(
            docs,
            ids=[f"{doc.source_id}:{idx}" for idx in range(len(docs))],
        )
        self.redis.client.set(
            f"{config.DIGEST_PREFIX}:{doc.source_id}",
            doc.page_content_digest,
        )

    def preprocess_doc(self, doc: HTMLDocumentRequest) -> list[DocumentModel]:
        return self.text_splitter.split_documents([preprocess(doc)])


RepositoryDep = Annotated[Repository, Depends(Repository)]
