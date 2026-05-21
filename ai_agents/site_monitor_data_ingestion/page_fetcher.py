from __future__ import annotations

import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Optional


DEFAULT_HEADERS = {
    "User-Agent": "page-watch-agent/0.1 (+https://local.agent)",
    "Accept-Language": "en-US,en;q=0.9",
}


@dataclass(slots=True)
class FetchResult:
    url: str
    status_code: int
    final_url: str
    fetched_at: datetime
    html: str
    text: str
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    not_modified: bool = False


def fetch_page(
    url: str,
    etag: str | None = None,
    last_modified: str | None = None,
    timeout: int = 30,
) -> FetchResult:
    headers = dict(DEFAULT_HEADERS)

    if etag:
        headers["If-None-Match"] = etag
    if last_modified:
        headers["If-Modified-Since"] = last_modified

    response = requests.get(url, headers=headers, timeout=timeout)

    if response.status_code == 304:
        return FetchResult(
            url=url,
            status_code=304,
            final_url=str(response.url or url),
            fetched_at=datetime.now(UTC),
            html="",
            text="",
            etag=response.headers.get("ETag", etag),
            last_modified=response.headers.get("Last-Modified", last_modified),
            not_modified=True,
        )

    response.raise_for_status()

    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)

    return FetchResult(
        url=url,
        status_code=response.status_code,
        final_url=str(response.url),
        fetched_at=datetime.now(UTC),
        html=html,
        text=text,
        etag=response.headers.get("ETag"),
        last_modified=response.headers.get("Last-Modified"),
        not_modified=False,
    )
