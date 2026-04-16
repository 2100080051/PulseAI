import os
import sys
import logging
import tweepy
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.db.client import get_supabase
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Access Twitter API credentials from .env
API_KEY = os.environ.get("TWITTER_API_KEY")
API_SECRET = os.environ.get("TWITTER_API_SECRET")
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET")
BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN")

def get_twitter_client() -> tweepy.Client:
    """Returns an authenticated Tweepy Client for API v2."""
    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
        logger.error("Missing Twitter API credentials.")
        return None
        
    client = tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_SECRET
    )
    return client

def post_daily_tweets():
    """Fetches today's approved stories and posts them to Twitter as a thread or individual tweets."""
    client = get_twitter_client()
    if not client:
        return {"status": "error", "message": "Twitter credentials missing."}
        
    sb = get_supabase()
    
    # Fetch top 3 recent approved stories
    # We limit to 3 so we don't spam the timeline
    stories_res = (sb.table("summaries")
               .select("*, articles(title, url)")
               .in_("status", ["approved", "edited"])
               .order("display_order", desc=False)
               .order("created_at", desc=True)
               .limit(3)
               .execute())
               
    stories = stories_res.data
    if not stories:
        return {"status": "no_stories", "message": "No approved stories to post."}
        
    tweeted_count = 0
    errors = []
    
    for idx, s in enumerate(stories):
        article = s.get('articles') or {}
        title = article.get('title', 'AI Update')
        url = article.get('url', 'https://pulseai.com')
        summary = s.get('summary_text', '')
        
        # Twitter character limit is 280. URLs consume 23 characters automatically via t.co.
        # We construct a tweet:
        # [Category] Title
        # 
        # (1-2 sentences of summary) ...
        # 
        # Read more: url
        category = s.get('category', 'AI News')
        
        # Build strict text
        tweet_text = f"🔥 {category}: {title}\n\n{summary}"
        
        # Truncate to leave space for URL (280 - 25 = 255 safe max)
        if len(tweet_text) > 230:
            tweet_text = tweet_text[:227] + "..."
            
        tweet_text += f"\n\n🔗 Read more: {url}"
        tweet_text += "\n#PulseAI #AI #TechNews"
        
        try:
            # Post tweet
            response = client.create_tweet(text=tweet_text)
            tweeted_count += 1
            logger.info(f"Successfully posted tweet ID: {response.data['id']}")
        except tweepy.errors.TweepyException as e:
            logger.error(f"Failed to post to Twitter: {e}")
            errors.append(str(e))
            
    if tweeted_count > 0:
        return {"status": "success", "tweets_sent": tweeted_count, "errors": errors}
    else:
        return {"status": "error", "message": f"Failed heavily: {errors}"}

if __name__ == "__main__":
    result = post_daily_tweets()
    print("Twitter Dispatch Result:", result)
