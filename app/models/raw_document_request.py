from typing import Literal

from pydantic.fields import Field

from app.models.base_document import BaseDocument
from app.models.document_metadata_model import DocumentMetadataModel


class RawDocumentRequest(BaseDocument):
    type: Literal["RAW"] = "RAW"

    metadata: DocumentMetadataModel = Field(default_factory=DocumentMetadataModel)
