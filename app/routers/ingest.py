import os
from pathlib import Path

from fastapi import APIRouter
from langchain_community.vectorstores.redis import Redis
from langchain_openai import OpenAIEmbeddings

from ..models.web_document import WebDocument

embeddings = OpenAIEmbeddings()


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
