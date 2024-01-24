import hashlib
import os
from pathlib import Path
from typing import TypedDict
from urllib.parse import urlparse, urlunparse

from fastapi import APIRouter
from langchain_community.vectorstores.redis import Redis
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from pydantic import Field

embeddings = OpenAIEmbeddings()


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


router = APIRouter()

index_schema = Path(os.path.dirname(__file__)).parent / "schema.yaml"

rds = Redis(
    redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/"),
    index_name="document",
    embedding=embeddings,
    index_schema=index_schema,
)


@router.post("/ingest", description="Ingest a document")
def ingest_doc(doc: WebDocument) -> str:
    ids = rds.add_documents([doc], ids=[doc.source_id()])
    return ids[0]
