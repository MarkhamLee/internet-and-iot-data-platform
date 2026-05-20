# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
# Content extraction pipeline for the data ingestion side of the
# site monitoring agent.
from __future__ import annotations

import re
from bs4 import BeautifulSoup
from typing import Any


def _normalize_text(value: str) -> str:
    value = value.strip()
    value = re.sub(r"\s+", " ", value)
    return value


def extract_review_payload(fetch_result, target) -> dict[str, Any]:
    soup = BeautifulSoup(fetch_result.html, "html.parser")

    selector_hits: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for selector in target.css_selectors:
        for node in soup.select(selector)[:10]:
            text = _normalize_text(node.get_text(" ", strip=True))
            if not text:
                continue

            key = (selector, text)
            if key in seen:
                continue
            seen.add(key)

            selector_hits.append({
                "selector": selector,
                "text": text[:500],
            })

    selector_hits.sort(key=lambda item: (item["selector"], item["text"]))

    lowered = fetch_result.text.lower()
    pattern_hits = sorted(
        {
            pattern
            for pattern in target.include_text_patterns
            if pattern.lower() in lowered
        }
    )

    button_texts = sorted(
        {
            _normalize_text(button.get_text(" ", strip=True))[:200]
            for button in soup.select("button,"
                                      "input[type='submit'],"
                                      "input[type='button']")[:30]
            if _normalize_text(button.get_text(" ", strip=True))
        }
    )

    return {
        "url": str(fetch_result.url),
        "final_url": str(fetch_result.final_url),
        "fetched_at": fetch_result.fetched_at.isoformat(),
        "selector_hits": selector_hits,
        "pattern_hits": pattern_hits,
        "button_texts": button_texts,
        "page_text_excerpt": _normalize_text(fetch_result.text[:12000]),
        "desired_state_description": target.desired_state_description,
        "undesired_state_description": target.undesired_state_description,
        "custom_prompt": target.custom_prompt,
    }
