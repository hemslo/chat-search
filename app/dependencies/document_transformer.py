from collections.abc import Sequence
from itertools import chain
from typing import Annotated, Any

from fastapi import Depends
from langchain_core.documents import BaseDocumentTransformer, Document
from langchain_text_splitters import (
    HTMLHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
    TextSplitter,
)

from app import config

HEADER_TO_TEXT = {
    "h1": "#",
    "h2": "##",
    "h3": "###",
    "h4": "####",
    "h5": "#####",
    "h6": "######",
}


class HTMLHeaderTransformer(BaseDocumentTransformer):
    def __init__(
        self,
        text_splitter: TextSplitter,
        html_splitter: HTMLHeaderTextSplitter,
    ):
        super().__init__()
        self.text_splitter = text_splitter
        self.html_splitter = html_splitter

    def _populate_headers(self, document: Document, metadata: dict) -> Document:
        headers = [h for h, _ in self.html_splitter.headers_to_split_on]
        header_lines = [
            f"{HEADER_TO_TEXT[header]} {header_content}"
            for header in headers
            if (header_content := document.metadata.get(header))
        ]
        page_content = "\n".join(header_lines + [document.page_content])
        return Document(
            page_content=page_content,
            metadata=document.metadata | metadata,
        )

    def _transform_document(self, document: Document) -> Sequence[Document]:
        docs = self.html_splitter.split_text(document.page_content)
        docs = self.text_splitter.split_documents(docs)
        return [self._populate_headers(d, document.metadata) for d in docs]

    def transform_documents(
        self,
        documents: Sequence[Document],
        **kwargs: Any,
    ) -> Sequence[Document]:
        return list(chain.from_iterable(self._transform_document(d) for d in documents))


html_header_transformer = HTMLHeaderTransformer(
    text_splitter=RecursiveCharacterTextSplitter(
        chunk_size=config.TEXT_SPLIT_CHUNK_SIZE,
        chunk_overlap=config.TEXT_SPLIT_CHUNK_OVERLAP,
    ),
    html_splitter=HTMLHeaderTextSplitter(
        headers_to_split_on=[(h, h) for h in config.HEADERS_TO_SPLIT_ON]
    ),
)


def get_document_transformer() -> BaseDocumentTransformer:
    return html_header_transformer


DocumentTransformerDep = Annotated[
    BaseDocumentTransformer, Depends(get_document_transformer)
]
