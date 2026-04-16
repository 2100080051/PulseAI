import os
import sys
import logging
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.db.client import get_supabase

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def delete_old_podcasts():
    """
    Supabase limits free storage to 1GB.
    User Business Rule: Past week podcasts get deleted automatically on Thursdays.
    For simplicity, this function scans the 'podcasts' bucket and deletes any file
    that is strictly older than 6 days (meaning old week's cycle is wiped).
    """
    sb = get_supabase()
    try:
        files = sb.storage.from_("podcasts").list()
        
        if not files:
            logger.info("No files in podcasts bucket to scan.")
            return

        now = datetime.now(timezone.utc)
        to_delete = []

        for f in files:
            # metadata 'created_at' looks like '2026-04-16T19:40:09.568Z'
            created_str = f.get('created_at')
            if not created_str:
                continue
                
            try:
                # Handle varying precision in isoformat
                created_str = created_str.replace("Z", "+00:00")
                created_at = datetime.fromisoformat(created_str)
            except ValueError:
                continue

            age_days = (now - created_at).days
            
            # If the video is 6 days or older, stage for deletion
            if age_days >= 6:
                to_delete.append(f['name'])

        if to_delete:
            logger.info(f"Found {len(to_delete)} expired podcasts. Schedulling deletion off Supabase...")
            sb.storage.from_("podcasts").remove(to_delete)
            logger.info(f"Successfully deleted {to_delete}")
        else:
            logger.info("All podcast files in the Cloud are fresh. No clean up required.")

    except Exception as e:
        logger.error(f"Failed to scrub Supabase Podcast Bucket: {e}")

if __name__ == "__main__":
    delete_old_podcasts()
