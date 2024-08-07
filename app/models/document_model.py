from pydantic import Field

from app.models.base_document import BaseDocument
from app.models.document_metadata_model import DocumentMetadataModel


class DocumentModel(BaseDocument):
    metadata: DocumentMetadataModel = Field(default_factory=DocumentMetadataModel)
