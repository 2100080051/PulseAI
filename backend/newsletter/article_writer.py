import os
import sys
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.db.client import get_supabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_openrouter_llm():
    """Returns a ChatOpenAI instance configured for OpenRouter."""
    return ChatOpenAI(
        model="google/gemini-2.0-flash-001", # High quality for long form synthesis
        openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.7,
        max_tokens=4000, # Increased for long articles
        default_headers={
            "HTTP-Referer": "https://pulseai.com",
            "X-Title": "PulseAI"
        }
    )

def fetch_summaries_for_article(days: int = 7, category: Optional[str] = None) -> List[Dict]:
    """Fetch approved/edited summaries from the last X days."""
    try:
        sb = get_supabase()
        start_date = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
        
        query = (
            sb.table("summaries")
            .select("*, articles(title, source, category)")
            .gte("edition_date", start_date)
            .in_("status", ["approved", "edited"])
            .order("edition_date", desc=True)
        )
        
        if category and category != "All":
            query = query.eq("category", category)
            
        result = query.execute()
        return result.data
    except Exception as e:
        logger.error(f"Failed to fetch summaries for article: {e}")
        return []

def generate_long_form_article(summaries: List[Dict], topic_hint: str = "") -> str:
    """Synthesize a collection of news summaries into a professional LinkedIn article."""
    if not summaries:
        return "Not enough data to generate an article. Please approve more stories first!"

    llm = get_openrouter_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a Senior AI Analyst and Thought Leader on LinkedIn.
Your job is to write a comprehensive, long-form 'State of AI' article (1000+ words) based on a collection of recent news stories.

ARTICLE STRUCTURE:
1. PUNCHY TITLE: A compelling, click-worthy headline.
2. EXECUTIVE SUMMARY: A brief overview of the major shifts seen in the news.
3. THEMATIC SECTIONS: Group the news stories into logical themes (e.g., 'The LLM Arms Race', 'Enterprise Adoption', 'Regulatory Landscape').
4. DEEP ANALYSIS: For each theme, don't just list facts. Explain the 'SO WHAT'—how these developments affect businesses and professionals.
5. PREDICTIONS: Based on these stories, what should we expect in the next 30 days?
6. CONCLUSION & CALL TO ACTION: A final wrap-up and a question to encourage comments.

STYLE RULES:
- Professional, analytical, and visionary.
- Use subheadings, bullet points, and bold text for readability.
- NO '***' SYMBOLS.
- NO MARKDOWN HORIZONTAL RULES.
- Use clear spacing between paragraphs."""),
        ("human", "Topic/Focus: {topic_hint}\n\nRecent Stories and Summaries:\n{stories_text}")
    ])
    
    stories_text = ""
    for idx, s in enumerate(summaries, 1):
        article = s.get('articles') or {}
        stories_text += f"--- Story {idx} ---\n"
        stories_text += f"Title: {article.get('title')}\n"
        stories_text += f"Category: {article.get('category')}\n"
        stories_text += f"Summary: {s.get('summary_text')}\n\n"
        
    chain = prompt | llm | StrOutputParser()
    
    logger.info(f"Generating long-form article from {len(summaries)} stories...")
    return chain.invoke({
        "topic_hint": topic_hint or "Weekly AI Industry Update",
        "stories_text": stories_text
    })

if __name__ == "__main__":
    # Quick test
    summaries = fetch_summaries_for_article(days=7)
    if summaries:
        article = generate_long_form_article(summaries)
        print(article[:500] + "...")
    else:
        print("No summaries found for the last 7 days.")
