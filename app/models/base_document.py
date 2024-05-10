import hashlib
from functools import cached_property
from typing import TypedDict

from langchain_core.documents import Document
from pydantic import Field


def sha256(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


class BaseDocumentMetadata(TypedDict):
    source: str


class BaseDocument(Document):
    metadata: BaseDocumentMetadata = Field(default_factory=BaseDocumentMetadata)

    @cached_property
    def source_id(self):
        return sha256(self.metadata["source"])

    @cached_property
    def page_content_digest(self):
        return sha256(self.page_content)

    class Config:
        keep_untouched = (cached_property,)
