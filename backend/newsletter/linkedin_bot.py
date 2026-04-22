import os
import sys
import logging
import requests
from datetime import date
from typing import List, Dict, Any

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
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

def get_openrouter_llm():
    """Returns a ChatOpenAI instance configured for OpenRouter."""
    return ChatOpenAI(
        model="google/gemini-2.0-flash-001",
        openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.7,
        max_tokens=2000,
        default_headers={
            "HTTP-Referer": "https://pulseai.com",
            "X-Title": "PulseAI"
        }
    )

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
               .in_("status", ["approved", "edited"])
               .order("display_order", desc=False)
               .order("created_at", desc=True))
               
    if selected_ids and len(selected_ids) > 0:
        query = query.in_("id", selected_ids)
    else:
        query = query.limit(3)
        
    stories_res = query.execute()
    stories = stories_res.data
    if not stories:
        return {"status": "no_stories", "message": "No approved stories to post."}
        
    post_text = generate_linkedin_draft(stories)
    main_article = stories[0].get('articles', {})
    
    return execute_linkedin_post(post_text, main_article)

def generate_linkedin_draft(stories: List[Dict], edition_type: str = "Morning") -> str:
    """Uses OpenRouter to ghostwrite a high-engagement, clean LinkedIn post."""
    llm = get_openrouter_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a viral LinkedIn Ghostwriter for PulseAI.
Your goal is to turn a list of AI news stories into a high-engagement, professional LinkedIn briefing.

CRITICAL FORMATTING RULES:
1. NO MARKDOWN SYMBOLS: Strictly forbidden to use '**' or '***' or '---'.
2. USE CLEAR SPACING: Leave an empty line between every major section.
3. USE BULLET POINTS: Use '•' or '🚀' or '🔹' for lists.
4. HEADLINES: Use ALL CAPS or Title Case for story headlines. Do NOT use bolding symbols.
5. NO MARKDOWN HR: Do not use --- or *** to separate news. Use whitespace.
6. TONE: Professional, slightly hype, but factual.
7. CTA: End with a question to drive comments.

Structure:
- Hook: A punchy one-liner about today's AI pulse.
- Stories: 3-5 stories, each with a headline and a 1-sentence takeaway.
- Closing: A brief summary of what this means for the industry.
- Question: A call to action.
- Hashtags: #PulseAI #AI #TechNews #GenerativeAI"""),
        ("human", "Edition: {edition_type}\n\nStories:\n{stories_text}")
    ])
    
    stories_text = ""
    for s in stories:
        article = s.get('articles') or {}
        stories_text += f"Headline: {article.get('title')}\nSummary: {s.get('summary_text')}\n\n"
        
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"edition_type": edition_type, "stories_text": stories_text})

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
