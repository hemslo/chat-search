from fastapi import APIRouter, Response, status

from ..dependencies.repository import RepositoryDep
from ..models.html_document_request import HTMLDocumentRequest
from ..models.raw_document_request import RawDocumentRequest

router = APIRouter()


@router.post("/ingest", description="Ingest a document", status_code=201)
def ingest_doc(
    doc: HTMLDocumentRequest | RawDocumentRequest,
    response: Response,
    repository: RepositoryDep,
) -> str:
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


@router.post(
    "/reset", description="Delete all documents and reset index", status_code=201
)
def destroy(
    repository: RepositoryDep,
) -> None:
    repository.reset()
