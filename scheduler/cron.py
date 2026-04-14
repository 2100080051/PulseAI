"""
PulseAI — Daily Pipeline Scheduler
Runs the full pipeline at 6:00 AM IST daily using APScheduler.
Can also be triggered manually: python scheduler/cron.py --run-now
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


def main():
    parser = argparse.ArgumentParser(description="PulseAI Pipeline Scheduler")
    parser.add_argument("--run-now", action="store_true", help="Run pipeline immediately")
    args = parser.parse_args()

    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    if args.run_now:
        logger.info("🏃 Running pipeline immediately (--run-now flag)")
        run_daily_pipeline()
        return

    # Schedule: 6 AM IST = 00:30 UTC
    # IST = UTC + 5:30, so 6:00 IST = 0:30 UTC
    scheduler = BlockingScheduler(timezone="Asia/Kolkata")
    scheduler.add_job(
        run_daily_pipeline,
        trigger=CronTrigger(hour=PIPELINE_RUN_HOUR, minute=0, timezone="Asia/Kolkata"),
        id="daily_pipeline",
        name="PulseAI Daily Pipeline",
        misfire_grace_time=3600,  # fire up to 1 hour late if missed
    )

    logger.info(f"⏰ PulseAI scheduler started — pipeline runs at {PIPELINE_RUN_HOUR}:00 IST daily")
    logger.info("Press Ctrl+C to stop.")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("🛑 Scheduler stopped.")


if __name__ == "__main__":
    main()
