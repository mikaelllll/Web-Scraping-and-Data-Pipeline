import asyncio
import html
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from xml.etree import ElementTree

import httpx
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from app.core.config import get_settings

TRACKING_PARAMETERS = {
    "fbclid",
    "gclid",
    "ref",
    "source",
    "utm_campaign",
    "utm_content",
    "utm_medium",
    "utm_source",
    "utm_term",
}


@dataclass(slots=True)
class CollectedArticle:
    title: str
    url: str
    published_at: datetime
    author: str | None = None
    excerpt: str | None = None
    categories: list[str] = field(default_factory=list)


def canonicalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    query = urlencode(
        [(k, v) for k, v in parse_qsl(parts.query) if k.lower() not in TRACKING_PARAMETERS]
    )
    return urlunsplit(
        (parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), query, "")
    )


def clean_text(value: str | None, limit: int = 800) -> str | None:
    if not value:
        return None
    text = BeautifulSoup(html.unescape(value), "html.parser").get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text)[:limit] or None


def parse_date(value: str | None) -> datetime:
    if not value:
        return datetime.now(UTC)
    try:
        parsed = date_parser.parse(value)
        return parsed.replace(tzinfo=parsed.tzinfo or UTC).astimezone(UTC)
    except (ValueError, TypeError, OverflowError):
        return datetime.now(UTC)


def _text(node: ElementTree.Element | None) -> str | None:
    return node.text.strip() if node is not None and node.text else None


def parse_feed(payload: str) -> list[CollectedArticle]:
    root = ElementTree.fromstring(payload)
    results: list[CollectedArticle] = []
    items = root.findall(".//item")
    if items:
        for item in items:
            title, link = _text(item.find("title")), _text(item.find("link"))
            if not title or not link:
                continue
            categories = [text for child in item.findall("category") if (text := _text(child))]
            results.append(
                CollectedArticle(
                    title=clean_text(title, 500) or title,
                    url=canonicalize_url(link),
                    author=_text(item.find("author")),
                    excerpt=clean_text(_text(item.find("description"))),
                    published_at=parse_date(_text(item.find("pubDate"))),
                    categories=categories,
                )
            )
        return results

    atom = "{http://www.w3.org/2005/Atom}"
    for entry in root.findall(f".//{atom}entry"):
        title_node = entry.find(f"{atom}title")
        link_node = entry.find(f"{atom}link")
        title = _text(title_node)
        link = link_node.get("href") if link_node is not None else None
        if not title or not link:
            continue
        author = _text(entry.find(f"{atom}author/{atom}name"))
        summary = _text(entry.find(f"{atom}summary")) or _text(entry.find(f"{atom}content"))
        published = _text(entry.find(f"{atom}published")) or _text(entry.find(f"{atom}updated"))
        categories = [
            term for node in entry.findall(f"{atom}category") if (term := node.get("term"))
        ]
        results.append(
            CollectedArticle(
                title=clean_text(title, 500) or title,
                url=canonicalize_url(link),
                author=author,
                excerpt=clean_text(summary),
                published_at=parse_date(published),
                categories=categories,
            )
        )
    return results


async def collect_feed(client: httpx.AsyncClient, feed_url: str) -> list[CollectedArticle]:
    response = await client.get(feed_url)
    response.raise_for_status()
    return parse_feed(response.text)


async def collect_all(
    sources: list[tuple[int, str]],
) -> list[tuple[int, list[CollectedArticle] | Exception]]:
    settings = get_settings()
    headers = {"User-Agent": "NewsPulse/1.0 (+educational portfolio; metadata collector)"}
    async with httpx.AsyncClient(
        timeout=settings.collector_timeout_seconds, headers=headers, follow_redirects=True
    ) as client:
        tasks = [collect_feed(client, url) for _, url in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    return [(source_id, result) for (source_id, _), result in zip(sources, results, strict=True)]
