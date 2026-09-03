"""Real multi-retailer product search via SerpApi's Google Shopping engine.

Replaces the old per-site httpx/BeautifulSoup scraping (which returned
guessed/fabricated data for JS-rendered sites like Flipkart/Croma/Reliance
Digital/Tata CLiQ, and got outright blocked by Amazon). SerpApi's Google
Shopping engine surfaces real, currently-listed offers -- price, rating,
review count, tags/badges, and a direct buy link -- for whichever Indian
retailers actually carry the searched product.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

import httpx
from dotenv import load_dotenv

# Load .env here too (not just in main.py) so this module sees SERPAPI_KEY
# correctly regardless of import order -- main.py imports this module
# before it calls load_dotenv() itself, which previously meant this file
# always read an empty key.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")
load_dotenv()

SERPAPI_URL = "https://serpapi.com/search"

# Stores we specifically care about when building the fallback "search this
# store directly" link if SerpApi has no key configured / returns nothing.
FALLBACK_STORES = [
    ("Amazon India", "https://www.amazon.in/s?k={q}"),
    ("Flipkart", "https://www.flipkart.com/search?q={q}"),
    ("Croma", "https://www.croma.com/searchB?q={q}"),
    ("Reliance Digital", "https://www.reliancedigital.in/search?q={q}"),
    ("Tata CLiQ", "https://www.tatacliq.com/search/?searchCategory=all&text={q}"),
]


def _clean_price(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"[\d,]+(?:\.\d+)?", str(value))
    return float(match.group(0).replace(",", "")) if match else None


def _clean_number(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"[\d,]+(?:\.\d+)?", str(value))
    return float(match.group(0).replace(",", "")) if match else None


def _tags_for(item: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    tag = item.get("tag")
    if isinstance(tag, str) and tag:
        tags.append(tag)
    extensions = item.get("extensions")
    if isinstance(extensions, list):
        tags.extend(str(e) for e in extensions if e)
    # de-dupe while preserving order
    seen = set()
    unique = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return unique[:5]


async def search_products(query: str) -> list[dict[str, Any]]:
    """Query SerpApi's Google Shopping (India) engine and normalize results.

    Returns a list of real listings: {store, title, price, mrp, rating,
    review_count, image, url, tags, delivery}. Empty list if no API key is
    configured, the request fails, or nothing was found.
    """
    api_key = os.getenv("SERPAPI_KEY", "")
    if not api_key:
        return []

    params = {
        "engine": "google_shopping",
        "q": query,
        "gl": "in",
        "hl": "en",
        "google_domain": "google.co.in",
        "api_key": api_key,
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(SERPAPI_URL, params=params)
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError):
        return []

    error = payload.get("error")
    if error:
        return []

    results: list[dict[str, Any]] = []
    for item in payload.get("shopping_results", []) or []:
        price = _clean_price(item.get("extracted_price") if item.get("extracted_price") is not None else item.get("price"))
        old_price = _clean_price(item.get("extracted_old_price") if item.get("extracted_old_price") is not None else item.get("old_price"))
        results.append({
            "store": item.get("source") or "Unknown Store",
            "title": item.get("title") or query,
            "price": price,
            "mrp": old_price,
            "rating": _clean_number(item.get("rating")),
            "review_count": item.get("reviews"),
            "image": item.get("thumbnail"),
            "url": item.get("product_link") or item.get("link"),
            "tags": _tags_for(item),
            "delivery": item.get("delivery"),
        })
    return results


async def scrape_stores(query: str) -> list[dict[str, Any]]:
    """Real product listings, shaped like {store, url, data, status}.

    Kept this name/shape for backward compatibility with main.py. Every
    entry with data.price/data.rating set came directly from SerpApi's
    live Google Shopping index -- nothing here is estimated or guessed.
    """
    products = await search_products(query)

    if products:
        return [
            {
                "store": p["store"],
                "url": p["url"],
                "data": {
                    "title": p["title"],
                    "price": p["price"],
                    "mrp": p["mrp"],
                    "rating": p["rating"],
                    "review_count": p["review_count"],
                    "image": p["image"],
                    "tags": p["tags"],
                    "delivery": p["delivery"],
                },
                "status": "live",
            }
            for p in products
        ]

    # No SerpApi key configured, or nothing found: return honest "search
    # this store yourself" links instead of pretending we have data.
    encoded = quote_plus(query.strip())
    return [
        {"store": name, "url": url_tpl.format(q=encoded), "data": None, "status": "unavailable"}
        for name, url_tpl in FALLBACK_STORES
    ]
