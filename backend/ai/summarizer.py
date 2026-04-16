"""
PulseAI — AI Summarization Engine
Uses LangChain + Groq (Llama 3.3 70B) to summarize articles.
Also classifies articles into categories.
"""

import os
import logging
from datetime import date

from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from dotenv import load_dotenv

from backend.db.client import get_supabase

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ── LLM Setup ────────────────────────────────────────────────────────────────

def get_llm() -> ChatGroq:
    """Return a Groq LLM instance using Llama 3.3 70B."""
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY,
        temperature=0.3,
        max_tokens=512,
    )


# ── Summarization Prompt ──────────────────────────────────────────────────────

SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert AI news journalist for PulseAI, a professional AI industry news platform.
Your job is to write crisp, factual, 3–5 sentence summaries of AI news articles.

Rules:
- Preserve all key facts: company names, people, numbers, dollar amounts, model names
- Explain WHY this matters to professionals in the last sentence
- Be objective and professional — no hype
- *Interlinking context*: If the article discusses geopolitics, technical news, or share markets, explain how it interlinks with broader global trends or local impacts carefully.
- Write in clear, simple English
- Do NOT include phrases like "In this article..." or "The article discusses..."
- Output ONLY the summary. Nothing else."""),

    ("human", """Article Title: {title}
Source: {source}
Category: {category}

Content:
{content}

Write a 3–5 sentence summary:"""),
])

SUMMARY_CHAIN = SUMMARY_PROMPT | get_llm() | StrOutputParser()


# ── Category Classification Prompt ───────────────────────────────────────────

CLASSIFY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a classifier for an AI news platform. Assign one category to the article.

Available categories:
- LLMs & Foundation Models
- AI Tools & Products
- Funding & Acquisitions
- AI in Healthcare
- AI Policy & Ethics
- India AI
- Research & Papers
- Technical News (World)
- Geopolitics
- Share Market (World)
- Share Market (India)

Respond with ONLY the category name. Nothing else."""),

    ("human", "Title: {title}\n\nContent snippet: {content}"),
])

CLASSIFY_CHAIN = CLASSIFY_PROMPT | get_llm() | StrOutputParser()


# ── Core Functions ────────────────────────────────────────────────────────────

def summarize_article(title: str, source: str, category: str, content: str) -> str:
    """Generate a 3–5 sentence summary for an article."""
    try:
        summary = SUMMARY_CHAIN.invoke({
            "title": title,
            "source": source,
            "category": category,
            "content": content[:3000],  # cap to avoid token limits
        })
        return summary.strip()
    except Exception as e:
        logger.error(f"  ❌ Summarization failed for '{title[:50]}': {e}")
        return ""


def classify_article(title: str, content: str) -> str:
    """Auto-classify an article into one of the 7 categories."""
    try:
        category = CLASSIFY_CHAIN.invoke({
            "title": title,
            "content": content[:500],
        })
        # Validate it's a known category
        valid_categories = [
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
            "Share Market (India)"
        ]
        return category.strip() if category.strip() in valid_categories else "AI Tools & Products"
    except Exception as e:
        logger.warning(f"  ⚠️ Classification failed: {e} — defaulting to AI Tools & Products")
        return "AI Tools & Products"


# ── Supabase Helpers ──────────────────────────────────────────────────────────

def get_pending_articles(limit: int = 50) -> list[dict]:
    """
    Fetch articles that don't yet have a summary in Supabase.
    Joins articles with summaries table to find unsummarized ones.
    """
    sb = get_supabase()
    # Get all article IDs that already have summaries
    existing = sb.table("summaries").select("article_id").execute()
    existing_ids = [r["article_id"] for r in existing.data]

    # Fetch articles not in that list
    query = sb.table("articles").select("*").order("fetched_at", desc=True).limit(limit)
    result = query.execute()

    # Filter out already-summarized articles
    return [a for a in result.data if a["id"] not in existing_ids]


def save_summary(article_id: str, summary_text: str, category: str) -> Optional[str]:
    """Save an AI-generated summary to Supabase with 'pending' status."""
    try:
        sb = get_supabase()
        result = sb.table("summaries").insert({
            "article_id": article_id,
            "summary_text": summary_text,
            "category": category,
            "status": "pending",
            "edition_date": str(date.today()),
        }).execute()
        return result.data[0]["id"]
    except Exception as e:
        logger.error(f"  ❌ Failed to save summary for article {article_id}: {e}")
        return None


# ── Main Summarizer Entry Point ───────────────────────────────────────────────

def run_summarizer(limit: int = 30) -> dict:
    """
    Summarize all pending (unsummarized) articles.
    Returns stats about how many were processed.
    """
    logger.info("=" * 60)
    logger.info("🤖 PulseAI Summarizer — Starting AI processing")
    logger.info("=" * 60)

    articles = get_pending_articles(limit=limit)
    logger.info(f"📋 Found {len(articles)} articles to summarize")

    success_count = 0
    fail_count = 0

    for i, article in enumerate(articles, 1):
        title = article["title"]
        source = article["source"]
        content = article.get("raw_content", "")
        category = article.get("category", "AI Tools & Products")

        logger.info(f"[{i}/{len(articles)}] 🔄 {title[:65]}")

        if not content:
            logger.warning(f"  ⚠️ No content — skipping")
            fail_count += 1
            continue

        # Optionally re-classify using LLM (improves accuracy)
        if category == "AI Tools & Products":
            category = classify_article(title, content)

        summary = summarize_article(title, source, category, content)

        if summary:
            summary_id = save_summary(article["id"], summary, category)
            if summary_id:
                success_count += 1
                logger.info(f"  ✅ Summary saved")
            else:
                fail_count += 1
        else:
            fail_count += 1

    logger.info("=" * 60)
    logger.info(f"✅ Summarization complete: {success_count} success, {fail_count} failed")
    logger.info("=" * 60)

    return {"success": success_count, "failed": fail_count}


if __name__ == "__main__":
    from typing import Optional
    stats = run_summarizer()
    print(f"\n🎉 Done! {stats['success']} summaries generated.")
