import os
import sys
import logging
from datetime import datetime, timezone, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from backend.db.client import get_supabase
from backend.audio.generator import generate_podcast_audio
from backend.audio.video_generator import generate_mp4_from_audio

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def fetch_ignored_weekly_summaries() -> list[dict]:
    """Retrieve all pending summaries from the last 7 days."""
    try:
        sb = get_supabase()
        seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).date().isoformat()
        
        result = (
            sb.table("summaries")
            .select("*, articles(title, source)")
            .gte("edition_date", seven_days_ago)
            .eq("status", "pending")
            .execute()
        )
        return result.data
    except Exception as e:
        logger.error(f"Failed to fetch weekly summaries: {e}")
        return []

def write_weekend_script(summaries: list[dict]) -> str:
    """Use Groq to synthesize the best of the neglected stories."""
    if not summaries:
        return "Hey everyone, welcome to the PulseAI Weekend recap! We actually covered all the major news during the week, so there's no leftover stories today. Enjoy your weekend!"

    groq_api_key = os.environ.get("GROQ_API_KEY")
    llm = ChatGroq(
        api_key=groq_api_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0.8,
        max_tokens=6000
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are the host of 'PulseAI Weekend Digest'. 
Your job is to look at a massive list of news stories that were skipped during the weekday episodes, and pick only the 5 most absolutely fascinating, weird, or high-impact 'hidden gem' stories.
Discard the boring enterprise or minor update stories.

Rules:
1. Start organically: 'Hey guys, welcome to the PulseAI Weekend Digest! During the week we focus on the biggest headlines, but today we dive into the hidden gems you might have completely missed...'
2. Be incredibly conversational. Use filler words like 'now', 'so', 'wow', 'listen to this' to make the TTS engine sound extremely realistic.
3. Keep it under 3 minutes total.
4. End smoothly: 'That's our weekend round-up! Have an awesome weekend and we'll see you on Monday!'
"""),
        ("user", "Here are {count} leftover stories from this week:\n\n{stories}")
    ])
    
    # Compress the input list to prevent hitting token caps if they skipped 500 stories
    stories_text = ""
    for idx, s in enumerate(summaries[:100], 1):
        title = s.get('articles', {}).get('title', 'Unknown Title')
        summary = s.get('summary_text', '')
        stories_text += f"---\nHeadline: {title}\nSummary: {summary}\n"
        
    chain = prompt | llm
    logger.info(f"Writing script from {len(summaries)} leftover stories...")
    
    res = chain.invoke({
        "count": len(summaries),
        "stories": stories_text
    })
    return res.content

def run_weekend_digest():
    """Fetches articles, writes script, renders MP3 and MP4."""
    logger.info("Starting Weekend Digest Protocol...")
    articles = fetch_ignored_weekly_summaries()
    
    if len(articles) > 0:
        logger.info(f"Found {len(articles)} ignored stories this week!")
        script = write_weekend_script(articles)
        logger.info("Script written! Synthesizing audio...")
        
        audio_path = generate_podcast_audio(script, "pulseai_weekend.mp3")
        if audio_path:
            logger.info("Audio saved. Constructing weekend Video File...")
            video_path = generate_mp4_from_audio(audio_path, output_path="pulseai_weekend_video.mp4")
            logger.info(f"Weekend Pipeline Complete! Saved to {video_path}")
            return {"status": "success", "audio": audio_path, "video": video_path}
    else:
        logger.info("No unused articles found in the last 7 days.")
        return {"status": "no_stories"}

if __name__ == "__main__":
    run_weekend_digest()
