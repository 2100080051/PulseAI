"""
Global Pulse AI — Daily Pipeline & LinkedIn Scheduler
Pipeline: runs at 6:00 AM IST daily.
LinkedIn Auto-Post: runs at 4:00 PM IST daily.
Manual trigger: python scheduler/cron.py --run-now
                python scheduler/cron.py --post-linkedin
"""

import sys
import os
import logging
import argparse
from datetime import datetime, timezone, timedelta

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/pipeline.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

PIPELINE_RUN_HOUR = int(os.getenv("PIPELINE_RUN_HOUR", 6))  # 6 AM IST by default


def run_daily_pipeline():
    """
    Full daily pipeline:
    1. Aggregate articles from all sources
    2. Summarize with Groq/LangChain
    """
    logger.info("=" * 70)
    logger.info(f"⏰ PIPELINE START — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    logger.info("=" * 70)

    try:
        from backend.aggregator.fetcher import run_aggregator
        agg_stats = run_aggregator()
        logger.info(f"📡 Aggregation done: {agg_stats['total_saved']} new articles")
    except Exception as e:
        logger.error(f"❌ Aggregation FAILED: {e}", exc_info=True)
        return

    try:
        from backend.ai.summarizer import run_summarizer
        sum_stats = run_summarizer()
        logger.info(f"🤖 Summarization done: {sum_stats['success']} summaries")
    except Exception as e:
        logger.error(f"❌ Summarization FAILED: {e}", exc_info=True)
        return

    logger.info("=" * 70)
    logger.info(
        f"✅ PIPELINE COMPLETE — "
        f"Articles: {agg_stats['total_saved']} | "
        f"Summaries: {sum_stats['success']}"
    )
    logger.info("=" * 70)
    logger.info("👉 Open the editorial dashboard to review and approve stories.")


def run_linkedin_autopost(edition_type: str = "Evening"):
    """
    Runs at 4 PM IST daily.
    Fetches approved stories, ghostwrites a viral post via Groq/OpenRouter,
    then auto-posts to LinkedIn personal + company profiles.
    """
    logger.info("=" * 70)
    logger.info(f"📣 LINKEDIN AUTO-POST START — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    logger.info("=" * 70)

    try:
        from backend.newsletter.linkedin_bot import blast_linkedin
        result = blast_linkedin()

        if result.get("status") == "success":
            logger.info(f"✅ LinkedIn auto-post SUCCESS — posted to {result.get('posted_count')} profiles.")
        elif result.get("status") == "no_stories":
            logger.warning("⚠️ No approved stories found. Skipping LinkedIn post.")
        else:
            logger.error(f"❌ LinkedIn auto-post FAILED: {result.get('message')}")
    except Exception as e:
        logger.error(f"❌ LinkedIn auto-post FAILED with exception: {e}", exc_info=True)


def main():
    parser = argparse.ArgumentParser(description="Global Pulse AI Scheduler")
    parser.add_argument("--run-now", action="store_true", help="Run morning pipeline immediately")
    parser.add_argument("--post-linkedin", action="store_true", help="Run LinkedIn auto-post immediately")
    args = parser.parse_args()

    os.makedirs("logs", exist_ok=True)

    if args.run_now:
        logger.info("🏃 Running pipeline immediately (--run-now flag)")
        run_daily_pipeline()
        return

    if args.post_linkedin:
        logger.info("📣 Running LinkedIn auto-post immediately (--post-linkedin flag)")
        run_linkedin_autopost()
        return

    scheduler = BlockingScheduler(timezone="Asia/Kolkata")

    # Job 1: Morning pipeline at 6 AM IST
    scheduler.add_job(
        run_daily_pipeline,
        trigger=CronTrigger(hour=PIPELINE_RUN_HOUR, minute=0, timezone="Asia/Kolkata"),
        id="daily_pipeline",
        name="Global Pulse AI — Morning Pipeline",
        misfire_grace_time=3600,
    )

    # Job 2: LinkedIn auto-post at 4 PM IST
    scheduler.add_job(
        run_linkedin_autopost,
        trigger=CronTrigger(hour=16, minute=0, timezone="Asia/Kolkata"),
        id="linkedin_autopost",
        name="Global Pulse AI — LinkedIn Auto-Post (4 PM IST)",
        misfire_grace_time=1800,
    )

    logger.info(f"⏰ Scheduler started — Pipeline at {PIPELINE_RUN_HOUR}:00 IST | LinkedIn at 16:00 IST")
    logger.info("Press Ctrl+C to stop.")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("🛑 Scheduler stopped.")


if __name__ == "__main__":
    main()
