import hashlib
from typing import TypedDict
from urllib.parse import urlparse, urlunparse

from langchain_core.documents import Document
from pydantic import Field, validator

DOC_FIELDS = [
    "source",
    "title",
    "description",
    "language",
    "content",
]


class WebDocumentMetadata(TypedDict):
    source: str
    title: str
    description: str
    language: str


class WebDocument(Document):
    metadata: WebDocumentMetadata = Field(default_factory=WebDocumentMetadata)

    def source_id(self):
        return hashlib.sha256(self.metadata["source"].encode()).hexdigest()

    @validator("metadata", pre=True)
    def validate_metadata(cls, metadata):
        metadata["source"] = cls._normalize_url(metadata["source"])
        return metadata

    @staticmethod
    def _normalize_url(url) -> str:
        parsed_url = urlparse(url)
        return urlunparse(
            (
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                parsed_url.query,
                "",
            )
        )
