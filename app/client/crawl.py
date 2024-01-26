#!/usr/bin/env python
import argparse
import asyncio
import os
from pprint import pprint

from aiohttp import TCPConnector, ClientSession
from bs4 import BeautifulSoup
from langchain_community.document_loaders import SitemapLoader
from langchain_core.documents import Document

from app.models.web_document import WebDocumentMetadata


def meta_function(meta: dict, soup: BeautifulSoup) -> WebDocumentMetadata:
    title = soup.find("title")
    description = soup.find("meta", attrs={"name": "description"})
    html = soup.find("html")
    return {
        "source": meta["loc"],
        "title": title.get_text() if title else "",
        "description": str(description.get("content", "")) if description else "",
        "language": str(html.get("lang", "")) if html else "",
    }


async def ingest_doc(
    doc: Document,
    ingest_url: str,
    session: ClientSession,
    headers: dict[str, str],
) -> tuple[str, bool]:
    async with session.post(
        ingest_url,
        json=doc.dict(),
        headers=headers,
    ) as response:
        return doc.metadata["source"], response.ok


async def ingest(
    docs: list[Document],
    ingest_url: str,
    ingest_concurrency: int,
    auth_token: str,
) -> dict[str, bool]:
    headers = {"Authorization": f"Bearer {auth_token}"}
    connector = TCPConnector(limit=ingest_concurrency)
    async with ClientSession(connector=connector) as session:
        results = await asyncio.gather(
            *(ingest_doc(doc, ingest_url, session, headers) for doc in docs),
        )
        return dict(results)


def crawl(
    sitemap_url: str,
    crawl_concurrency: int,
    ingest_url: str,
    ingest_concurrency: int,
    auth_token: str,
) -> None:
    docs = SitemapLoader(
        sitemap_url,
        meta_function=meta_function,
        requests_per_second=crawl_concurrency,
    ).load()

    result = asyncio.run(ingest(docs, ingest_url, ingest_concurrency, auth_token))

    pprint(result, sort_dicts=True)
    failed_urls = [url for url, ok in result.items() if not ok]
    if failed_urls:
        raise Exception(f"Failed to ingest {len(failed_urls)} URLs: {failed_urls}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl.")
    parser.add_argument(
        "--sitemap-url",
        type=str,
        help="The URL of the sitemap to crawl.",
        required=True,
    )
    parser.add_argument(
        "--crawl-concurrency",
        type=int,
        default=os.environ.get("CRAWL_CONCURRENCY", 10),
        help="The number of concurrent crawl requests to make.",
    )
    parser.add_argument(
        "--ingest-url",
        type=str,
        default=os.environ.get("INGEST_URL", "http://localhost:8000/ingest"),
        help="The URL of the ingest endpoint.",
    )
    parser.add_argument(
        "--ingest-concurrency",
        type=int,
        default=os.environ.get("INGEST_CONCURRENCY", 10),
        help="The number of concurrent ingest requests to make.",
    )
    parser.add_argument(
        "--auth-token",
        type=str,
        default=os.environ.get("AUTH_TOKEN"),
        help="The auth token to use for the ingest endpoint.",
    )
    args = parser.parse_args()
    crawl(**vars(args))


if __name__ == "__main__":
    main()
