from fastapi import APIRouter, Response, status

from ..dependencies.repository import RepositoryDep
from ..models.web_document import WebDocument

router = APIRouter()


@router.post("/ingest", description="Ingest a document", status_code=201)
def ingest_doc(doc: WebDocument, response: Response, repository: RepositoryDep) -> str:
    source_id = doc.source_id()
    existing = repository.get(source_id)
    if existing == doc:
        response.status_code = status.HTTP_304_NOT_MODIFIED
        return source_id
    repository.save(doc)
    if existing is not None:
        response.status_code = status.HTTP_200_OK
    return source_id
