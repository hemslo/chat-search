import os
from pathlib import Path

from fastapi import APIRouter, Response, status
from langchain_community.vectorstores.redis import Redis
from langchain_openai import OpenAIEmbeddings

from ..models.web_document import WebDocument, DOC_FIELDS

embeddings = OpenAIEmbeddings()


router = APIRouter()

index_schema = Path(os.path.dirname(__file__)).parent / "schema.yaml"

rds = Redis(
    redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/"),
    index_name="document",
    embedding=embeddings,
    index_schema=index_schema,
)


@router.post("/ingest", description="Ingest a document", status_code=201)
def ingest_doc(doc: WebDocument, response: Response) -> str:
    source_id = doc.source_id()
    existing = _get_doc(source_id)

    if existing == doc:
        response.status_code = status.HTTP_304_NOT_MODIFIED
        return source_id

    rds.add_documents([doc], ids=[source_id])

    if existing is not None:
        response.status_code = status.HTTP_200_OK

    return source_id


def _get_doc(source_id: str) -> WebDocument | None:
    values = rds.client.hmget(f"{rds.key_prefix}:{source_id}", DOC_FIELDS)
    if all(v is None for v in values):
        return None
    return WebDocument(
        metadata=dict(zip(DOC_FIELDS[:-1], values[:-1])),
        page_content=values[-1],
    )
