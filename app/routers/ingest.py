from fastapi import APIRouter, Response, status

from ..dependencies.repository import RepositoryDep
from ..models.web_document import WebDocument

router = APIRouter()


@router.post("/ingest", description="Ingest a document", status_code=201)
def ingest_doc(doc: WebDocument, response: Response, repository: RepositoryDep) -> str:
    digest = repository.get_digest(doc.source_id)
    match digest:
        case None:
            repository.save(doc)
            response.status_code = status.HTTP_201_CREATED
        case doc.page_content_digest:
            response.status_code = status.HTTP_304_NOT_MODIFIED
        case _:
            repository.save(doc)
            response.status_code = status.HTTP_200_OK
    return doc.source_id
