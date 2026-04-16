"""
PulseAI — FastAPI Backend
Serves approved summaries, search, category filters, and newsletter subscribe.
"""

import os
import sys
from datetime import date, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.db.client import get_supabase

load_dotenv()

app = FastAPI(
    title="PulseAI API",
    description="Backend API for PulseAI Daily AI News Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CATEGORIES = [
    "LLMs & Foundation Models",
    "AI Tools & Products",
    "Funding & Acquisitions",
    "AI in Healthcare",
    "AI Policy & Ethics",
    "India AI",
    "Research & Papers",
    "Technical News (World)",
    "Geopolitics",
    "Share Market (World)",
    "Share Market (India)",
]


# ── Models ────────────────────────────────────────────────────────────────────

class SubscribeRequest(BaseModel):
    email: EmailStr
    platform: str = "web"


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "PulseAI API is live", "version": "1.0.0"}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/categories")
def get_categories():
    """Return list of all available categories."""
    sb = get_supabase()
    # Get counts per category from approved summaries
    result = sb.table("summaries").select("category").in_("status", ["approved", "edited"]).execute()
    counts = {}
    for row in result.data:
        c = row["category"]
        counts[c] = counts.get(c, 0) + 1
    return [{"name": c, "count": counts.get(c, 0)} for c in CATEGORIES]


@app.get("/api/summaries")
def get_summaries(
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    days: int = Query(7, ge=1, le=30),
):
    """
    Get approved summaries with optional category filter.
    Paginated. Returns summaries from last N days.
    """
    sb = get_supabase()
    since = str(date.today() - timedelta(days=days))
    offset = (page - 1) * limit

    query = (
        sb.table("summaries")
        .select("*, articles(title, url, source, image_url)")
        .in_("status", ["approved", "edited"])
        .gte("edition_date", since)
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
    )

    if category:
        query = query.eq("category", category)

    result = query.execute()
    return {
        "page": page,
        "limit": limit,
        "data": result.data,
        "has_more": len(result.data) == limit,
    }


@app.get("/api/summaries/latest")
def get_latest(limit: int = Query(10, ge=1, le=20)):
    """Get the latest approved summaries (for hero section)."""
    sb = get_supabase()
    result = (
        sb.table("summaries")
        .select("*, articles(title, url, source, image_url)")
        .in_("status", ["approved", "edited"])
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data


@app.get("/api/summaries/stats")
def get_stats():
    """Get platform statistics."""
    sb = get_supabase()
    articles_count = sb.table("articles").select("id", count="exact").execute()
    summaries_count = sb.table("summaries").select("id", count="exact").in_("status", ["approved", "edited"]).execute()
    editions_count = sb.table("editions").select("id", count="exact").execute()
    return {
        "total_articles": articles_count.count or 0,
        "total_summaries": summaries_count.count or 0,
        "total_editions": editions_count.count or 0,
        "sources": 15,
        "categories": len(CATEGORIES),
    }


@app.get("/api/search")
def search(q: str = Query(..., min_length=2)):
    """Full-text search across summaries and article titles."""
    sb = get_supabase()
    result = (
        sb.table("summaries")
        .select("*, articles(title, url, source, image_url)")
        .in_("status", ["approved", "edited"])
        .text_search("fts", q)
        .order("created_at", desc=True)
        .limit(20)
        .execute()
    )
    return {"query": q, "results": result.data, "count": len(result.data)}


@app.get("/api/editions")
def get_editions(limit: int = Query(10, ge=1, le=30)):
    """Get list of published editions."""
    sb = get_supabase()
    result = (
        sb.table("editions")
        .select("*")
        .eq("status", "published")
        .order("edition_date", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data


@app.post("/api/subscribe")
def subscribe(req: SubscribeRequest):
    """Subscribe email to PulseAI newsletter."""
    sb = get_supabase()
    try:
        existing = sb.table("subscribers").select("id, is_active").eq("email", req.email).execute()
        if existing.data:
            sub = existing.data[0]
            if sub["is_active"]:
                return {"message": "Already subscribed!", "status": "already_exists"}
            # Re-activate if unsubscribed
            sb.table("subscribers").update({"is_active": True, "unsubscribed_at": None}).eq("email", req.email).execute()
            return {"message": "Welcome back! You've been re-subscribed.", "status": "reactivated"}

        sb.table("subscribers").insert({
            "email": req.email,
            "platform": req.platform,
            "is_active": True,
        }).execute()
        return {"message": "Successfully subscribed to PulseAI!", "status": "subscribed"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
