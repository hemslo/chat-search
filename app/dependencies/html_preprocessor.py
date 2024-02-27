from bs4 import BeautifulSoup

from app.models.document_model import DocumentMetadataModel, DocumentModel
from app.models.html_document_request import HTMLDocumentRequest


def _get_title(soup: BeautifulSoup) -> str | None:
    if title := soup.find("title"):
        return title.get_text()
    return None


def _get_description(soup: BeautifulSoup) -> str | None:
    if description := soup.find("meta", attrs={"name": "description"}):
        return description.get("content", None)
    return None


def _get_language(soup: BeautifulSoup) -> str | None:
    if html := soup.find("html"):
        return html.get("lang", None)
    return None


def _metadata_extractor(soup: BeautifulSoup, source: str) -> DocumentMetadataModel:
    metadata = {
        "source": source,
        "title": _get_title(soup),
        "description": _get_description(soup),
        "language": _get_language(soup),
    }

    return {k: v for k, v in metadata.items() if v}


def _page_content_extractor(soup: BeautifulSoup) -> str:
    return soup.get_text(separator="\n\n", strip=True)


def preprocess(doc: HTMLDocumentRequest) -> DocumentModel:
    soup = BeautifulSoup(doc.page_content, "lxml")
    metadata = _metadata_extractor(soup, doc.metadata["source"])
    page_content = _page_content_extractor(soup)

    return DocumentModel(
        metadata=metadata,
        page_content=page_content,
    )
