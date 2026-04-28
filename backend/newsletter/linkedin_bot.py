import os
import sys
import logging
import requests
from datetime import date
from typing import List, Dict, Any

from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.db.client import get_supabase
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ACCESS_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN")

# The user explicitly requested posting to both personal and company!
# Replace this with the actual company ID extracted from the URL
COMPANY_URN = "urn:li:organization:114304591"

LINKEDIN_PROFILE_URL = "https://www.linkedin.com/in/sri-sai-nikshith-mummidivarapu-b842a2246"

SYSTEM_PROMPT = """You are a viral LinkedIn Ghostwriter for Global Pulse AI.
Your goal is to turn a list of AI news stories into a high-engagement, professional LinkedIn briefing.

CRITICAL FORMATTING RULES:
1. NO MARKDOWN: Do NOT use ** or *** or --- symbols. LinkedIn ignores markdown.
2. SPACING: Leave an empty line between every story block.
3. EMOJIS: Use relevant emojis (🚀 💰 ⚠️ 📈 🧠 🎬 🏥) before each headline.
4. LENGTH: STRICTLY under 2,500 characters total. Be concise.
5. LINKS: Include the original article URL under each story as: 🔗 [url]
6. STORIES: Cover ALL provided stories, one punchy sentence each.
7. CTA: End with exactly this line: "Follow me for daily AI intelligence 👉 {profile_url}"
8. HASHTAGS: Add EXACTLY 15 real, relevant hashtags. NO made-up tags. NO recursive tags like #AIFuture or #AIFutureLeaders. Use only well-known tags like #AI #TechNews #Startups.
9. DO NOT hallucinate, invent, or repeat hashtags.

Structure:
- Hook (1 punchy sentence)
- Stories (emoji + HEADLINE + 1 sentence + 🔗 url)
- 1 engagement question
- CTA line
- Exactly 15 hashtags""".format(profile_url=LINKEDIN_PROFILE_URL)

def get_personal_urn():
    """Fetch the authenticated user's URN from LinkedIn /v2/userinfo endpoint."""
    if not ACCESS_TOKEN:
        return None
        
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Connection": "Keep-Alive"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        person_id = data.get("sub")
        return f"urn:li:person:{person_id}"
    else:
        logger.error(f"Failed to fetch personal URN: {response.text}")
        return None

def post_to_linkedin(author_urn: str, text: str, article_url: str, article_title: str, image_url: str = ""):
    """Post an article to LinkedIn as the given author URN."""
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    
    share_content = {
        "shareCommentary": {
            "text": text
        }
    }
    
    if image_url:
        media_block = {
            "status": "READY",
            "originalUrl": article_url,
            "title": {
                "text": article_title[:200]
            },
            "thumbnails": [{"url": image_url}]
        }
        share_content["shareMediaCategory"] = "ARTICLE"
        share_content["media"] = [media_block]
    else:
        share_content["shareMediaCategory"] = "NONE"
        
    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": share_content
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        return True, response.json()
    else:
        logger.error(f"Failed to post for author {author_urn}: {response.text}")
        return False, response.text

def blast_linkedin(selected_ids=None):
    """Fetches approved stories and posts them to LinkedIn as a structured mini-newsletter."""
    if not ACCESS_TOKEN:
        return {"status": "error", "message": "LINKEDIN_ACCESS_TOKEN not found in .env! Run get_linkedin_token.py first."}
        
    personal_urn = get_personal_urn()
    if not personal_urn:
        return {"status": "error", "message": "Invalid token or failed to fetch LinkedIn profile."}
        
    authors = [personal_urn]
    
    sb = get_supabase()
    
    query = (sb.table("summaries")
               .select("*, articles(title, url, image_url)")
               .eq("edition_date", date.today().isoformat())
               .in_("status", ["approved", "edited"])
               .order("created_at", desc=True))

    if selected_ids and len(selected_ids) > 0:
        query = query.in_("id", selected_ids)
        
    stories_res = query.execute()
    stories = stories_res.data
    if not stories:
        return {"status": "no_stories", "message": "No approved stories to post."}
        
    post_text = generate_linkedin_draft(stories)
    main_article = stories[0].get('articles', {})
    
    return execute_linkedin_post(post_text, main_article)

def generate_linkedin_draft(stories: List[Dict], edition_type: str = "Morning") -> str:
    """Ghostwrites a viral LinkedIn post. Tries Groq first, falls back to OpenRouter (Gemini)."""
    if not stories:
        return ""

    date_str = date.today().strftime('%B %d, %Y')

    # Build the stories payload with URLs included
    stories_text = ""
    for idx, s in enumerate(stories, 1):
        article = s.get('articles') or {}
        title = article.get('title', 'Update')
        summary = s.get('summary_text', '')
        url = article.get('url', '')
        stories_text += f"Story {idx}:\nHeadline: {title}\nSummary: {summary}\nURL: {url}\n\n"

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Edition: {edition_type}\nDate: {date_str}\n\nStories:\n{stories_text}")
    ])
    invoke_input = {"edition_type": edition_type, "date_str": date_str, "stories_text": stories_text}

    # --- TIER 1: Groq (Llama-3, fastest & free) ---
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key:
        try:
            logger.info("🚀 Trying Groq (Llama-3.3-70B)...")
            llm = ChatGroq(temperature=0.7, model_name="llama-3.3-70b-versatile", groq_api_key=groq_key)
            draft = (prompt | llm | StrOutputParser()).invoke(invoke_input)
            logger.info("✅ Groq draft successful.")
            return draft
        except Exception as e:
            logger.warning(f"⚠️ Groq failed ({e}). Falling back to OpenRouter...")

    # --- TIER 2: OpenRouter — Google Gemini 2.0 Flash (free tier) ---
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    if openrouter_key:
        try:
            logger.info("🔄 Trying OpenRouter (Google Gemini 2.0 Flash)...")
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openrouter_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://globalpulseai.com",
                    "X-Title": "Global Pulse AI",
                },
                json={
                    "model": "google/gemini-2.0-flash-exp:free",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Edition: {edition_type}\nDate: {date_str}\n\nStories:\n{stories_text}"}
                    ],
                    "max_tokens": 900,
                    "temperature": 0.7,
                },
                timeout=30
            )
            if resp.status_code == 200:
                draft = resp.json()["choices"][0]["message"]["content"]
                logger.info("✅ OpenRouter (Gemini) draft successful.")
                return draft
            else:
                logger.error(f"OpenRouter error {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.error(f"❌ OpenRouter also failed: {e}")

    return "❌ All LLM providers failed. Check GROQ_API_KEY / OPENROUTER_API_KEY in .env"

def execute_linkedin_post(text: str, main_article: Dict = None):
    """Executes the post to both personal and company profiles."""
    personal_urn = get_personal_urn()
    if not personal_urn:
        return {"status": "error", "message": "Failed to fetch personal URN."}
        
    results = []
    
    # 1. Post to Personal Profile
    success_p, resp_p = post_to_linkedin(
        author_urn=personal_urn,
        text=text,
        article_url=main_article.get("url", "https://pulseai.com") if main_article else "https://pulseai.com",
        article_title=main_article.get("title", "PulseAI Daily Update") if main_article else "PulseAI Daily Update",
        image_url=main_article.get("image_url", "") if main_article else ""
    )
    results.append(success_p)
    
    # 2. Post to Company Profile
    success_c, resp_c = post_to_linkedin(
        author_urn=COMPANY_URN,
        text=text,
        article_url=main_article.get("url", "https://pulseai.com") if main_article else "https://pulseai.com",
        article_title=main_article.get("title", "PulseAI Daily Update") if main_article else "PulseAI Daily Update",
        image_url=main_article.get("image_url", "") if main_article else ""
    )
    results.append(success_c)
    
    if any(results):
        return {"status": "success", "posted_count": sum(results)}
    else:
        return {"status": "error", "message": "Failed to post to any profile."}

if __name__ == "__main__":
    result = blast_linkedin()
    print("LinkedIn Dispatch Result:", result)
