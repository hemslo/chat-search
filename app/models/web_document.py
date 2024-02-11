import hashlib
from functools import cached_property
from typing import TypedDict
from urllib.parse import urlparse, urlunparse

from langchain_core.documents import Document
from pydantic import Field, validator


class WebDocumentMetadata(TypedDict):
    source: str
    title: str
    description: str
    language: str


def sha256(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()


class WebDocument(Document):
    metadata: WebDocumentMetadata = Field(default_factory=WebDocumentMetadata)

    @cached_property
    def source_id(self):
        return sha256(self.metadata["source"])

    @cached_property
    def page_content_digest(self):
        return sha256(self.page_content)

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

    class Config:
        keep_untouched = (cached_property,)
