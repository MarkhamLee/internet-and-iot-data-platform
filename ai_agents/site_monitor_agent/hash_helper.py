# (C) Markham Lee 2023 - 2026
# https://github.com/MarkhamLee/internet-and-iot-data-platform
import hashlib
import json
import re
from typing import Any


def normalize_text(value: str) -> str:
    value = value.strip()
    value = re.sub(r"\s+", " ", value)
    return value


def canonicalize_for_hash(payload: dict[str, Any]) -> dict[str, Any]:
    selector_hits = [
        {
            "selector": item["selector"],
            "text": normalize_text(item["text"]),
        }
        for item in payload.get("selector_hits", [])
    ]

    return {
        "final_url": payload.get("final_url"),
        "pattern_hits": sorted(payload.get("pattern_hits", [])),
        "selector_hits": selector_hits,
        "page_text_excerpt": normalize_text(payload.
                                            get("page_text_excerpt", "")),
    }


def compute_content_hash(payload: dict[str, Any]) -> str:
    canonical = canonicalize_for_hash(payload)
    encoded = json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
