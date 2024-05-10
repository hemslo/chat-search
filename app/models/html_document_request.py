from typing import Literal
from urllib.parse import urlparse, urlunparse

from pydantic.class_validators import validator

from app.models.base_document import BaseDocument


class HTMLDocumentRequest(BaseDocument):
    type: Literal["HTML"] = "HTML"

    @validator("metadata", pre=True)
    def validate_metadata(cls, metadata):
        metadata["source"] = cls._normalize_url(metadata["source"])
        return metadata

    @staticmethod
    def _normalize_url(url) -> str:
        parsed_url = urlparse(url)
        return urlunparse(
            (
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                parsed_url.query,
                "",
            )
        )
