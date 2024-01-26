import hashlib
from typing import TypedDict
from urllib.parse import urlparse, urlunparse

from langchain_core.documents import Document
from pydantic import Field


class WebDocumentMetadata(TypedDict):
    source: str
    title: str
    description: str
    language: str


class WebDocument(Document):
    metadata: WebDocumentMetadata = Field(default_factory=WebDocumentMetadata)

    def source_id(self):
        source = self.normalize_url(self.metadata["source"])
        return hashlib.sha256(source.encode()).hexdigest()

    @staticmethod
    def normalize_url(url) -> str:
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
