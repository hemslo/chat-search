#!/usr/bin/env python
import argparse

from bs4 import BeautifulSoup
from langchain_community.document_loaders import SitemapLoader


def meta_function(meta: dict, soup: BeautifulSoup) -> dict:
    title = soup.find("title")
    description = soup.find("meta", attrs={"name": "description"})
    html = soup.find("html")
    return {
        "source": meta["loc"],
        "title": title.get_text() if title else "",
        "description": description.get("content", "") if description else "",
        "language": html.get("lang", "") if html else "",
        **meta,
    }


def crawl(sitemap_url: str):
    docs = SitemapLoader(
        sitemap_url,
        meta_function=meta_function,
    ).load()
    return docs


def main():
    parser = argparse.ArgumentParser(description="Crawl.")
    parser.add_argument(
        "--sitemap-url",
        type=str,
        help="The URL of the sitemap to crawl.",
    )
    args = parser.parse_args()
    if args.sitemap_url:
        crawl(args.sitemap_url)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
