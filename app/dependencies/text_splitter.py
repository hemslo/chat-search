from typing import Annotated

from fastapi import Depends
from langchain.text_splitter import RecursiveCharacterTextSplitter, TextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=4000,
    chunk_overlap=200,
)


def get_text_splitter() -> TextSplitter:
    return text_splitter


TextSplitterDep = Annotated[TextSplitter, Depends(get_text_splitter)]
