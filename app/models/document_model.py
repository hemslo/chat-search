from typing import NotRequired, TypedDict

from pydantic import Field

from app.models.base_document import BaseDocument


class DocumentMetadataModel(TypedDict):
    source: str
    title: NotRequired[str]
    description: NotRequired[str]
    language: NotRequired[str]


class DocumentModel(BaseDocument):
    metadata: DocumentMetadataModel = Field(default_factory=DocumentMetadataModel)
