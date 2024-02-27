from typing import Literal

from app.models.base_document import BaseDocument


class HTMLDocumentRequest(BaseDocument):
    type: Literal["HTML"] = "HTML"
