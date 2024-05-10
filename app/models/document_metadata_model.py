from typing import NotRequired, TypedDict


class DocumentMetadataModel(TypedDict):
    source: str
    title: NotRequired[str]
    description: NotRequired[str]
    language: NotRequired[str]
