# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Page fetcher for site monitoring agent
from __future__ import annotations
import requests
from bs4 import BeautifulSoup
from datetime import datetime, UTC
from schemas import FetchResult


DEFAULT_HEADERS = {
    "User-Agent": "page-watch-agent/0.1 (+https://local.agent)",
    "Accept-Language": "en-US,en;q=0.9",
}


# TODO: change this to try/except and add logging for errors
def fetch_page(url: str, timeout: int = 30) -> FetchResult:
    response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
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
        last_modified=response.headers.get("Last-Modified"),)
