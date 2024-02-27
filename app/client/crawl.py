#!/usr/bin/env python
import argparse
import asyncio
import os
from collections.abc import Iterable
from pprint import pprint
from typing import Any

from aiohttp import TCPConnector, ClientSession
from bs4 import BeautifulSoup
from langchain_community.document_loaders import (
    SitemapLoader,
    RecursiveUrlLoader,
)
from langchain_community.document_loaders.base import BaseLoader
from tqdm.asyncio import tqdm_asyncio

from app.models.base_document import BaseDocumentMetadata
from app.models.html_document_request import HTMLDocumentRequest


def meta_function(meta: dict, _content: Any) -> BaseDocumentMetadata:
    return {
        "source": meta["loc"],
    }


def metadata_extractor(_raw_html: str, url: str) -> BaseDocumentMetadata:
    return {
        "source": url,
    }


def parsing_function(content: BeautifulSoup) -> str:
    return str(content)


def extractor(content: str) -> str:
    return parsing_function(BeautifulSoup(content, "lxml"))


async def ingest_doc(
    doc: HTMLDocumentRequest,
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


async def ingest_doc_with_concurrency(
    doc: HTMLDocumentRequest,
    ingest_url: str,
    session: ClientSession,
    headers: dict[str, str],
    semaphore: asyncio.Semaphore,
) -> tuple[str, bool]:
    async with semaphore:
        return await ingest_doc(doc, ingest_url, session, headers)


async def ingest(
    docs: Iterable[HTMLDocumentRequest],
    ingest_url: str,
    ingest_concurrency: int,
    auth_token: str,
) -> dict[str, bool]:
    headers = {"Authorization": f"Bearer {auth_token}"}
    semaphore = asyncio.Semaphore(ingest_concurrency)
    connector = TCPConnector(limit=ingest_concurrency)
    async with ClientSession(connector=connector) as session:
        tasks = [
            asyncio.ensure_future(
                ingest_doc_with_concurrency(
                    doc, ingest_url, session, headers, semaphore
                )
            )
            for doc in docs
        ]
        results = await tqdm_asyncio.gather(
            *tasks, desc="Ingesting", ascii=True, mininterval=1
        )
        return dict(results)


def build_loader(
    url: str,
    max_depth: int,
    sitemap_url: str,
    exclude_urls: list[str] | None,
    crawl_concurrency: int,
) -> BaseLoader:
    if sitemap_url:
        return SitemapLoader(
            sitemap_url,
            filter_urls=[url] if url else None,
            meta_function=meta_function,
            parsing_function=parsing_function,
            requests_per_second=crawl_concurrency,
            default_parser="lxml",
        )
    return RecursiveUrlLoader(
        url=url,
        max_depth=max_depth,
        extractor=extractor,
        metadata_extractor=metadata_extractor,
        exclude_dirs=exclude_urls,
        use_async=crawl_concurrency > 1,
    )


def crawl(
    url: str | None,
    sitemap_url: str | None,
    exclude_urls: list[str] | None,
    max_depth: int,
    crawl_concurrency: int,
    ingest_url: str,
    ingest_concurrency: int,
    auth_token: str,
) -> None:
    loader = build_loader(
        url=url,
        max_depth=max_depth,
        sitemap_url=sitemap_url,
        exclude_urls=exclude_urls,
        crawl_concurrency=crawl_concurrency,
    )
    docs = (
        HTMLDocumentRequest(
            page_content=doc.page_content,
            metadata=doc.metadata,
        )
        for doc in loader.load()
    )

    result = asyncio.run(ingest(docs, ingest_url, ingest_concurrency, auth_token))

    pprint(result, sort_dicts=True)
    failed_urls = [url for url, ok in result.items() if not ok]
    if failed_urls:
        raise Exception(f"Failed to ingest {len(failed_urls)} URLs: {failed_urls}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl.")
    parser.add_argument(
        "--url",
        type=str,
        help="The URL to crawl.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=os.environ.get("MAX_DEPTH", 2),
        help="The maximum depth to crawl. (No effect when use sitemap.)",
    )
    parser.add_argument(
        "--sitemap-url",
        type=str,
        help="The URL of the sitemap to crawl.",
    )
    parser.add_argument(
        "--exclude-urls",
        type=str,
        nargs="*",
        help="The URLs to exclude from the crawl. (No effect when use sitemap.)",
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
    if args.url is None and args.sitemap_url is None:
        parser.error("You must specify either --url or --sitemap-url.")
    crawl(**vars(args))


if __name__ == "__main__":
    main()
