"""FastAPI backend for SmartBuy AI -- a generic multi-retailer product finder.

Given any product query, fetches real live listings across Indian
e-commerce retailers (via SerpApi's Google Shopping engine, see
scraper.py) and picks a winner using a transparent price/rating/review
composite score -- never fabricated numbers.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
# Load .env BEFORE importing scraper -- scraper.py also loads it defensively,
# but doing it here first too means no module ever reads SERPAPI_KEY before
# it's actually in the environment, regardless of import order.
load_dotenv(ROOT / ".env")
load_dotenv()

from scraper import scrape_stores  # noqa: E402

app = FastAPI(title="SmartBuy AI API", version="3.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    maxBudget: float | None = Field(default=None, gt=0)


class ReviewRequest(BaseModel):
    review: str = Field(min_length=1)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


def _as_number(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(",", "").strip())
    except ValueError:
        return None


def _composite_score(row: dict[str, Any], price_lo: float, price_hi: float) -> float:
    """Transparent 0..1 score: cheaper + higher rated + more reviews wins.

    Nothing here is fabricated -- it's a plain weighted blend of the real
    price/rating/review_count values SerpApi returned for this row.
    """
    price = row.get("price")
    if price is not None and price_hi > price_lo:
        price_score = 1 - (price - price_lo) / (price_hi - price_lo)
    elif price is not None:
        price_score = 1.0
    else:
        price_score = 0.3

    rating = row.get("rating")
    rating_score = (min(rating, 5.0) / 5.0) if rating is not None else 0.4

    review_count = _as_number(row.get("review_count"))
    review_score = min(1.0, math.log10(review_count + 1) / 4) if review_count else 0.2

    return round(price_score * 0.45 + rating_score * 0.35 + review_score * 0.20, 4)


def build_comparison(query: str, live: list[dict[str, Any]], max_budget: float | None) -> dict[str, Any]:
    """Build the comparison response from real listings -- no guessed facts."""
    rows: list[dict[str, Any]] = []
    for item in live:
        data = item.get("data") or {}
        price = data.get("price")
        mrp = data.get("mrp")
        rows.append({
            "platform": item["store"],
            "product_name": data.get("title") or query,
            "price": price,
            "mrp": mrp,
            "discount_pct": round((mrp - price) / mrp * 100) if mrp and price else None,
            "rating": data.get("rating"),
            "review_count": data.get("review_count"),
            "tags": data.get("tags") or [],
            "image": data.get("image"),
            "delivery_speed": data.get("delivery"),
            "best_deal_here": False,
            "product_url": item["url"],
            "scrape_status": item.get("status", "unavailable"),
        })

    priced_rows = [row for row in rows if isinstance(row["price"], (int, float))]

    # Prefer rows within budget when one was given and at least one row fits.
    eligible = priced_rows
    budget_note = None
    if max_budget:
        within_budget = [row for row in priced_rows if row["price"] <= max_budget]
        if within_budget:
            eligible = within_budget
        elif priced_rows:
            budget_note = f"Nothing found at or under your ₹{max_budget:,.0f} budget -- showing the closest options instead."

    winner = None
    if eligible:
        prices = [row["price"] for row in eligible]
        price_lo, price_hi = min(prices), max(prices)
        scored = sorted(
            ({**row, "_score": _composite_score(row, price_lo, price_hi)} for row in eligible),
            key=lambda r: r["_score"],
            reverse=True,
        )
        winner = scored[0]
        remaining = scored[1:]

        # Budget pick: cheapest of the remaining options.
        budget_pick = min(remaining, key=lambda r: r["price"]) if remaining else None
        # Premium pick: highest-rated of what's left (excluding the budget pick).
        premium_candidates = [r for r in remaining if r is not budget_pick]
        premium_pick = max(premium_candidates, key=lambda r: (r.get("rating") or 0, r["price"])) if premium_candidates else None
    else:
        budget_pick = None
        premium_pick = None

    for row in rows:
        row["best_deal_here"] = bool(winner) and row["platform"] == winner["platform"] and row["product_url"] == winner["product_url"]

    runner_ups = []
    if budget_pick:
        runner_ups.append({
            "category": "Cheapest Alternative",
            "title": budget_pick["product_name"],
            "platform": budget_pick["platform"],
            "price": budget_pick["price"],
            "mrp": budget_pick["mrp"],
            "rating": budget_pick["rating"],
            "buy_url": budget_pick["product_url"],
            "highlight": f"Lowest price among the other listings found (₹{budget_pick['price']:,.0f}).",
        })
    if premium_pick:
        runner_ups.append({
            "category": "Highest Rated Alternative",
            "title": premium_pick["product_name"],
            "platform": premium_pick["platform"],
            "price": premium_pick["price"],
            "mrp": premium_pick["mrp"],
            "rating": premium_pick["rating"],
            "buy_url": premium_pick["product_url"],
            "highlight": f"Best rating among the other listings found ({premium_pick['rating']}★)." if premium_pick.get("rating") else "A strong alternative listing.",
        })

    strategic_insights = [
        "Prices, ratings, and review counts shown are live listings pulled just now -- they can change by the time you check out.",
        "Open the buy link to confirm final price, stock, seller rating, and delivery before purchasing.",
    ]
    if budget_note:
        strategic_insights.insert(0, budget_note)
    if not live or not any(item.get("status") == "live" for item in live):
        strategic_insights.append(
            "No live product-data API key is configured, so these are direct search links to each retailer instead of live prices -- add SERPAPI_KEY to .env to enable real comparisons."
        )

    if winner:
        winner_out = {
            "title": winner["product_name"],
            "best_platform": winner["platform"],
            "best_price": winner["price"],
            "mrp": winner["mrp"],
            "discount_pct": winner["discount_pct"],
            "rating": winner["rating"],
            "review_count": winner["review_count"],
            "tags": winner["tags"],
            "match_score": round(winner["_score"] * 100),
            "buy_url": winner["product_url"],
            "image_url": winner.get("image"),
            "verdict_headline": "Best overall match by price, rating, and review volume",
            "why_buy": f"₹{winner['price']:,.0f} at {winner['platform']}"
                       + (f" ({winner['rating']}★, {winner['review_count']} reviews)" if winner.get("rating") else "")
                       + " -- the strongest real listing found for this search.",
            "pros": (["Backed by a real, currently-live listing"]
                     + ([f"{winner['rating']}★ rating"] if winner.get("rating") else [])
                     + ([f"{winner['review_count']} reviews"] if winner.get("review_count") else [])),
            "cons": ["Prices and stock change quickly -- verify at checkout."],
            "warranty_delivery": winner.get("delivery_speed"),
            "key_specs": winner["tags"],
        }
    else:
        winner_out = {
            "title": query,
            "best_platform": None,
            "best_price": None,
            "mrp": None,
            "discount_pct": None,
            "rating": None,
            "review_count": None,
            "tags": [],
            "match_score": None,
            "buy_url": None,
            "image_url": None,
            "verdict_headline": "No live listings found for this search",
            "why_buy": "No retailer data could be retrieved for this query. Try a more specific product name, or search the links below directly.",
            "pros": [],
            "cons": [],
            "warranty_delivery": None,
            "key_specs": [],
        }

    return {
        "query": query,
        "is_real_time": bool(winner),
        "scrape_status": "live" if winner else ("unavailable" if live else "no_api_key"),
        "winner": winner_out,
        "runner_ups": runner_ups,
        "platform_comparison": rows,
        "aspect_ratings": [],
        "strategic_insights": strategic_insights,
    }


@app.post("/api/search")
async def search(request: SearchRequest) -> dict[str, Any]:
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Product search query is required.")
    live = await scrape_stores(query)
    return build_comparison(query, live, request.maxBudget)


@app.post("/api/analyze")
async def analyze(request: ReviewRequest) -> dict[str, Any]:
    review = request.review.strip()
    if not review:
        raise HTTPException(status_code=400, detail="Review text is required")
    key = os.getenv("GROQ_API_KEY")
    if key:
        prompt = f'Return only JSON with sentiment_label, sentiment_score, and key_themes for this review: "{review}"'
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {key}"}, json={"model": "llama-3.1-8b-instant", "temperature": 0, "response_format": {"type": "json_object"}, "messages": [{"role": "user", "content": prompt}]})
                response.raise_for_status()
                return json.loads(response.json()["choices"][0]["message"]["content"])
        except (httpx.HTTPError, KeyError, json.JSONDecodeError):
            pass
    positive = {"good", "great", "excellent", "love", "quality", "comfortable", "fast"}
    negative = {"bad", "poor", "broken", "worst", "late", "damaged"}
    words = set(review.lower().split())
    score = max(-1.0, min(1.0, (len(words & positive) - len(words & negative)) / 5))
    return {"sentiment_label": "Positive" if score > 0.1 else "Negative" if score < -0.1 else "Neutral", "sentiment_score": round(score, 2), "key_themes": ["Product quality"]}
