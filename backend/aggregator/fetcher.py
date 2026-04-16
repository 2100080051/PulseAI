"""
PulseAI — News Aggregator
Pulls articles from RSS feeds and NewsAPI, deduplicates, stores to Supabase.
"""

import os
import hashlib
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

import feedparser
import requests
from dotenv import load_dotenv

from backend.db.client import get_supabase
from backend.aggregator.sources import RSS_FEEDS, NEWSAPI_QUERIES

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

NEWSAPI_KEY = os.getenv("NEWS_API_KEY")
MAX_ARTICLES = int(os.getenv("MAX_ARTICLES_PER_SOURCE", 10))


# ── Utilities ────────────────────────────────────────────────────────────────

def make_url_hash(url: str) -> str:
    """SHA-256 hash of URL — used as deduplication key."""
    return hashlib.sha256(url.strip().encode()).hexdigest()


def already_exists(url_hash: str) -> bool:
    """Check Supabase if this article URL hash already exists."""
    try:
        sb = get_supabase()
        result = sb.table("articles").select("id").eq("url_hash", url_hash).execute()
        return len(result.data) > 0
    except Exception as e:
        logger.warning(f"Dedup check failed for {url_hash}: {e}")
        return False


def save_article(
    url: str,
    title: str,
    source: str,
    category: str,
    raw_content: Optional[str] = None,
    image_url: Optional[str] = None,
) -> Optional[str]:
    """
    Insert a new article into Supabase. Returns article ID if inserted.
    Returns None if skipped (duplicate).
    """
    url_hash = make_url_hash(url)

    if already_exists(url_hash):
        logger.debug(f"  ↳ SKIP (duplicate): {title[:60]}")
        return None

    try:
        sb = get_supabase()
        result = sb.table("articles").insert({
            "url_hash": url_hash,
            "title": title,
            "url": url,
            "source": source,
            "raw_content": (raw_content or "")[:5000],  # cap content length
            "image_url": image_url,
            "category": category,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }).execute()

        article_id = result.data[0]["id"]
        logger.info(f"  ✅ SAVED [{category}]: {title[:70]}")
        return article_id

    except Exception as e:
        logger.error(f"  ❌ Failed to save article '{title[:50]}': {e}")
        return None


# ── RSS Aggregator ────────────────────────────────────────────────────────────

def fetch_rss_source(feed_config: dict) -> list[str]:
    """Fetch articles from a single RSS feed. Returns list of saved article IDs."""
    name = feed_config["name"]
    url = feed_config["url"]
    category = feed_config["category"]
    saved_ids = []

    logger.info(f"📡 Fetching RSS: {name}")

    try:
        feed = feedparser.parse(url)
        entries = feed.entries[:MAX_ARTICLES]

        for entry in entries:
            article_url = getattr(entry, "link", None)
            article_title = getattr(entry, "title", "Untitled")
            raw_content = getattr(entry, "summary", None) or getattr(entry, "description", None)
            
            image_url = None
            if "media_thumbnail" in entry and entry.media_thumbnail:
                image_url = entry.media_thumbnail[0]["url"]
            elif "media_content" in entry and entry.media_content:
                image_url = entry.media_content[0]["url"]

            if not article_url:
                continue

            article_id = save_article(
                url=article_url,
                title=article_title,
                source=name,
                category=category,
                raw_content=raw_content,
                image_url=image_url,
            )
            if article_id:
                saved_ids.append(article_id)

    except Exception as e:
        logger.error(f"  ❌ RSS fetch failed for {name}: {e}")

    return saved_ids


def fetch_all_rss() -> list[str]:
    """Fetch all RSS feeds. Returns all saved article IDs."""
    all_ids = []
    for feed in RSS_FEEDS:
        ids = fetch_rss_source(feed)
        all_ids.extend(ids)
    return all_ids


# ── NewsAPI Aggregator ────────────────────────────────────────────────────────

def fetch_newsapi_query(query_config: dict) -> list[str]:
    """Fetch articles from NewsAPI for a specific query. Returns saved article IDs."""
    q = query_config["q"]
    category = query_config["category"]
    saved_ids = []

    logger.info(f"📰 NewsAPI query: '{q}'")

    if not NEWSAPI_KEY:
        logger.warning("NEWS_API_KEY not set — skipping NewsAPI fetch")
        return []

    # Only fetch articles from last 24 hours
    from_date = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%S")

    try:
        resp = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": q,
                "from": from_date,
                "sortBy": "publishedAt",
                "language": "en",
                "pageSize": MAX_ARTICLES,
                "apiKey": NEWSAPI_KEY,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        for article in data.get("articles", []):
            article_url = article.get("url", "")
            article_title = article.get("title", "Untitled")
            raw_content = article.get("description", "") or article.get("content", "")
            image_url = article.get("urlToImage")
            source_name = article.get("source", {}).get("name", "NewsAPI")

            if not article_url or article_url == "https://removed.com":
                continue

            article_id = save_article(
                url=article_url,
                title=article_title,
                source=source_name,
                category=category,
                raw_content=raw_content,
                image_url=image_url,
            )
            if article_id:
                saved_ids.append(article_id)

    except requests.exceptions.HTTPError as e:
        if "426" in str(e):
            logger.warning(f"  ⚠️ NewsAPI free tier rate limit hit for '{q}' — skipping")
        else:
            logger.error(f"  ❌ NewsAPI HTTP error for '{q}': {e}")
    except Exception as e:
        logger.error(f"  ❌ NewsAPI fetch failed for '{q}': {e}")

    return saved_ids


def fetch_all_newsapi() -> list[str]:
    """Fetch all NewsAPI queries. Returns all saved article IDs."""
    all_ids = []
    for query in NEWSAPI_QUERIES:
        ids = fetch_newsapi_query(query)
        all_ids.extend(ids)
    return all_ids


# ── Main Aggregator Entry Point ───────────────────────────────────────────────

def run_aggregator() -> dict:
    """
    Run the full aggregation pipeline.
    Fetches from all RSS feeds + NewsAPI and stores new articles to Supabase.
    Returns summary stats.
    """
    logger.info("=" * 60)
    logger.info("🚀 PulseAI Aggregator — Starting pipeline")
    logger.info("=" * 60)

    rss_ids = fetch_all_rss()
    newsapi_ids = fetch_all_newsapi()
    total = len(rss_ids) + len(newsapi_ids)

    logger.info("=" * 60)
    logger.info(f"✅ Aggregation complete: {total} new articles saved")
    logger.info(f"   RSS: {len(rss_ids)}  |  NewsAPI: {len(newsapi_ids)}")
    logger.info("=" * 60)

    return {
        "total_saved": total,
        "rss_saved": len(rss_ids),
        "newsapi_saved": len(newsapi_ids),
        "article_ids": rss_ids + newsapi_ids,
    }


if __name__ == "__main__":
    results = run_aggregator()
    print(f"\n🎉 Done! {results['total_saved']} new articles fetched and stored.")
