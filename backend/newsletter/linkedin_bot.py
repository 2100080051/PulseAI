import os
import sys
import logging
import requests
from datetime import date

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
    
    media_block = {
        "status": "READY",
        "originalUrl": article_url,
        "title": {
            "text": article_title[:200]
        }
    }
    
    if image_url:
        media_block["thumbnails"] = [{"url": image_url}]
        
    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "ARTICLE",
                "media": [media_block]
            }
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
        
    # Build a structured, beautiful Newsletter post
    date_str = date.today().strftime("%B %d, %Y")
    
    post_text = f"📰 The PulseAI Daily Briefing — {date_str}\n"
    post_text += "Here are the most critical updates in Artificial Intelligence & Macro Tech Markets today:\n\n"
    
    for idx, story in enumerate(stories, 1):
        article = story.get('articles') or {}
        title = article.get('title', 'AI Update')
        category = story.get('category', 'AI News')
        
        # Make the summary concise for social
        summary = story.get('summary_text', '')
        if len(summary) > 200:
            summary = summary[:197] + "..."
            
        article_url = article.get('url', '')
            
        post_text += f"{idx}. 🚨 {title} ({category})\n"
        post_text += f"   ➤ {summary}\n"
        post_text += f"   🔗 Read more: {article_url}\n\n"
        
    # The primary CTA / Hero article to be the link preview
    main_article_url = stories[0].get('articles', {}).get('url', 'https://pulseai.com')
    main_article_title = stories[0].get('articles', {}).get('title', 'PulseAI Briefing')
    main_image_url = stories[0].get('articles', {}).get('image_url', '')

    post_text += "Read the full stories and subscribe to the daily email newsletter on our platform! 👇\n\n"
    
    # Tagging string calculation
    tag_string = "PulseAI"
    post_text += f"Automated & Curated by {tag_string}.\n\n"
    
    mention_start = post_text.find(tag_string)
    mention_length = len(tag_string)

    post_text += "#PulseAI #ArtificialIntelligence #TechNews #Innovation #MachineLearning #MacroMarkets"
    
    success_count = 0
    errors = []
    
    for author in authors:
        success, resp = post_to_linkedin(author, post_text, main_article_url, main_article_title, main_image_url)
        if success:
            success_count += 1
            print(f"SUCCESS: Posted to {author}")
            print(f"RAW RESPONSE ID: {resp.get('id', 'NONE')}")
        else:
            errors.append(f"Failed {author}: {resp}")
            print(f"FAILED to {author}: {resp}")
            
    if success_count > 0:
        return {"status": "success", "posted_count": success_count, "errors": errors}
    else:
        return {"status": "error", "message": str(errors)}

if __name__ == "__main__":
    result = blast_linkedin()
    print("LinkedIn Dispatch Result:", result)
