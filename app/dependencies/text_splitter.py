from typing import Annotated

from fastapi import Depends
from langchain.text_splitter import RecursiveCharacterTextSplitter, TextSplitter

from app import config

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=config.TEXT_SPLIT_CHUNK_SIZE,
    chunk_overlap=config.TEXT_SPLIT_CHUNK_OVERLAP,
)


def get_text_splitter() -> TextSplitter:
    return text_splitter


TextSplitterDep = Annotated[TextSplitter, Depends(get_text_splitter)]
