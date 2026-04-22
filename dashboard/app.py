"""
PulseAI — Editorial Dashboard (Streamlit)
The founder's interface to review, approve, edit, or reject AI summaries.
"""

import streamlit as st
from datetime import date, timedelta
from typing import Optional
import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.client import get_supabase

# ─── Page Config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Global Pulse AI Editorial Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* Dark editorial theme */
    .main { background-color: #0f1117; }
    
    .stApp { background: linear-gradient(135deg, #0f1117 0%, #1a1d2e 100%); }
    
    /* Story card */
    .story-card {
        background: #1e2130;
        border: 1px solid #2d3048;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
    
    .category-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    /* Status colors */
    .status-pending  { color: #f59e0b; }
    .status-approved { color: #10b981; }
    .status-rejected { color: #ef4444; }
    .status-edited   { color: #3b82f6; }
    
    /* Stats cards */
    .metric-card {
        background: #1e2130;
        border: 1px solid #2d3048;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    
    h1, h2, h3 { color: #f1f5f9; }
    
    .source-tag {
        font-size: 11px;
        color: #64748b;
        margin-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Category Colors ──────────────────────────────────────────────────────────

CATEGORY_COLORS = {
    "LLMs & Foundation Models": "#6366f1",
    "AI Tools & Products": "#0ea5e9",
    "Funding & Acquisitions": "#10b981",
    "AI in Healthcare": "#f59e0b",
    "AI Policy & Ethics": "#ef4444",
    "India AI": "#f97316",
    "Research & Papers": "#8b5cf6",
}

CATEGORIES = list(CATEGORY_COLORS.keys())

# ─── Supabase Helpers ─────────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def load_summaries(status_filter: str, edition_date: str) -> list[dict]:
    """Load summaries with their article info from Supabase."""
    try:
        sb = get_supabase()
        query = (
            sb.table("summaries")
            .select("*, articles(title, url, source, category)")
            .eq("edition_date", edition_date)
            .order("created_at", desc=True)
        )
        if status_filter != "all":
            query = query.eq("status", status_filter)

        result = query.execute()
        return result.data
    except Exception as e:
        st.error(f"Failed to load summaries: {e}")
        return []


def update_summary(summary_id: str, new_text: str, new_category: str, new_status: str):
    """Update a summary's text, category, and status."""
    from datetime import datetime, timezone
    sb = get_supabase()
    sb.table("summaries").update({
        "summary_text": new_text,
        "category": new_category,
        "status": new_status,
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", summary_id).execute()


def get_stats(edition_date: str) -> dict:
    """Get count of summaries by status for today's edition."""
    try:
        sb = get_supabase()
        result = sb.table("summaries").select("status").eq("edition_date", edition_date).execute()
        counts = {"pending": 0, "approved": 0, "rejected": 0, "edited": 0}
        for row in result.data:
            s = row["status"]
            counts[s] = counts.get(s, 0) + 1
        return counts
    except:
        return {"pending": 0, "approved": 0, "rejected": 0, "edited": 0}


def get_approved_summaries(edition_date: str) -> list[dict]:
    """Get all approved summaries for LinkedIn newsletter export."""
    sb = get_supabase()
    result = (
        sb.table("summaries")
        .select("*, articles(title, url, source)")
        .eq("edition_date", edition_date)
        .in_("status", ["approved", "edited"])
        .order("display_order")
        .execute()
    )
    return result.data


def run_pipeline(edition_date_str: str):
    """Trigger the full aggregation + summarization pipeline."""
    from backend.aggregator.fetcher import run_aggregator
    from backend.ai.summarizer import run_summarizer
    with st.spinner("🚀 Running aggregator..."):
        agg_stats = run_aggregator()
    with st.spinner("🤖 Running AI summarizer..."):
        sum_stats = run_summarizer(edition_date=edition_date_str)
    return agg_stats, sum_stats


# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚡ Global Pulse AI")
    st.markdown("**Editorial Dashboard**")
    st.divider()

    # Edition date picker
    # Allow +1 day because Cloud servers are in UTC while user is in IST (India)
    selected_date = st.date_input(
        "📅 Edition Date",
        value=date.today(),
        min_value=date.today() - timedelta(days=30),
        max_value=date.today() + timedelta(days=1),
    )
    edition_date_str = str(selected_date)

    st.divider()

    # Status filter
    status_filter = st.selectbox(
        "🔍 Filter by Status",
        options=["all", "pending", "approved", "edited", "rejected"],
        index=0,
    )

    st.divider()

    # Run pipeline button
    st.markdown("### 🔧 Pipeline")
    if st.button("▶️ Run Full Pipeline", use_container_width=True, type="primary"):
        try:
            agg_stats, sum_stats = run_pipeline(edition_date_str)
            st.success(
                f"✅ Done!\n\n"
                f"Fetched: {agg_stats['total_saved']} articles\n"
                f"Summarized: {sum_stats['success']} stories"
            )
            st.cache_data.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Pipeline error: {e}")

    st.divider()
    st.markdown("*Built by Nani · Global Pulse AI 2026*")


# ─── Main Content ─────────────────────────────────────────────────────────────

st.markdown("# ⚡ Global Pulse AI — Editorial Dashboard")
st.markdown(f"**Edition:** {selected_date.strftime('%B %d, %Y')} &nbsp;|&nbsp; Review and approve today's AI stories")

# Stats row
stats = get_stats(edition_date_str)
total = sum(stats.values())

with st.container(border=True):
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("📊 Total Stories", total)
    col2.metric("⏳ Pending", stats.get("pending", 0))
    col3.metric("✅ Approved", stats.get("approved", 0))
    col4.metric("✏️ Edited", stats.get("edited", 0))
    col5.metric("❌ Rejected", stats.get("rejected", 0))

st.write("")

# Create Tabs
tab_queue, tab_distribution = st.tabs(["📋 Editorial Queue", "🚀 Distribution Hub"])

with tab_queue:
    # Load summaries
    summaries = load_summaries(status_filter, edition_date_str)

    if not summaries:
        st.info(
            "📭 No summaries found for this date/filter.\n\n"
            "Run the pipeline from the sidebar to fetch and summarize today's AI news."
        )
    else:
        st.markdown(f"### 📋 Review Queue ({len(summaries)} stories)")

        for summary in summaries:
            article = summary.get("articles") or {}
            title = article.get("title", "Untitled")
            source = article.get("source", "Unknown")
            url = article.get("url", "#")
            category = summary.get("category", "AI Tools & Products")
            summary_id = summary["id"]
            current_status = summary["status"]
            current_text = summary["summary_text"]
            color = CATEGORY_COLORS.get(category, "#64748b")

            with st.expander(
                f"{'🟡' if current_status == 'pending' else '🟢' if current_status in ['approved','edited'] else '🔴'} "
                f"{title[:80]}",
                expanded=(current_status == "pending"),
            ):
                # Source + Category
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"<div class='source-tag'>📰 {source} &nbsp;|&nbsp; <a href='{url}' target='_blank'>Read Original ↗</a></div>", unsafe_allow_html=True)
                with col_b:
                    st.markdown(
                        f"<span style='background:{color};color:white;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600'>{category}</span>",
                        unsafe_allow_html=True,
                    )

                st.markdown("**AI Summary:**")
                new_text = st.text_area(
                    label="Summary",
                    value=current_text,
                    key=f"text_{summary_id}",
                    height=120,
                    label_visibility="collapsed",
                )

                new_category = st.selectbox(
                    "Category",
                    options=CATEGORIES,
                    index=CATEGORIES.index(category) if category in CATEGORIES else 0,
                    key=f"cat_{summary_id}",
                )

                # Action buttons
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                with btn_col1:
                    if st.button("✅ Approve", key=f"approve_{summary_id}", use_container_width=True, type="primary"):
                        status = "edited" if new_text != current_text else "approved"
                        update_summary(summary_id, new_text, new_category, status)
                        st.success("Approved!")
                        st.cache_data.clear()
                        st.rerun()
                with btn_col2:
                    if st.button("✏️ Save Edit", key=f"edit_{summary_id}", use_container_width=True):
                        update_summary(summary_id, new_text, new_category, "edited")
                        st.info("Saved as edited")
                        st.cache_data.clear()
                        st.rerun()
                with btn_col3:
                    if st.button("❌ Reject", key=f"reject_{summary_id}", use_container_width=True):
                        update_summary(summary_id, current_text, new_category, "rejected")
                        st.warning("Rejected")
                        st.cache_data.clear()
                        st.rerun()

with tab_distribution:
    st.markdown("## 🚀 Multi-Channel Distribution Hub")
    st.info("Approve stories in the Editorial Queue tab first, then publish them to Email and Social Media here!")
    
    col_em, col_li = st.columns(2)
    
    with col_em:
        st.markdown("### 📧 Email Newsletter")
        with st.container(border=True):
            st.markdown("Blast today's approved stories to your **Resend** active subscriber list.")
            if st.button("🚀 Send Email Blast", use_container_width=True, type="primary"):
                from backend.newsletter.resend_mailer import blast_newsletter
                with st.spinner("Dispatching emails via Resend..."):
                    result = blast_newsletter()
                    if result.get("status") == "success":
                        st.success(f"✅ Sent to {result.get('emails_sent')} subscribers!")
                    elif result.get("status") == "no_stories":
                        st.warning("No approved stories for today.")
                    elif result.get("status") == "no_subscribers":
                        st.warning("No active email subscribers found.")
                    else:
                        st.error(f"Failed to send: {result.get('message')}")
                        
    with col_li:
        st.markdown("### 📤 LinkedIn Automation")
        with st.container(border=True):
            approved = get_approved_summaries(edition_date_str)
            if not approved:
                st.warning("No approved stories found.")
            else:
                st.markdown("Select stories for the **LinkedIn Daily Briefing**:")
                selected_linkedin_ids = []
                
                with st.expander("📝 Manage Stories Checklist", expanded=True):
                    for s in approved:
                        article = s.get('articles') or {}
                        title = article.get('title', 'Unknown')
                        if st.checkbox(f"🔗 {title}", value=True, key=f"li_post_{s['id']}"):
                            selected_linkedin_ids.append(s["id"])

                if st.button("🚀 Auto-Post to LinkedIn", use_container_width=True, type="primary"):
                    if not selected_linkedin_ids:
                        st.error("Select at least one story!")
                    else:
                        from backend.newsletter.linkedin_bot import blast_linkedin
                        with st.spinner("Posting to LinkedIn..."):
                            result = blast_linkedin(selected_ids=selected_linkedin_ids)
                            if result.get("status") == "success":
                                st.success(f"✅ Posted Successfully!")
                            elif result.get("status") == "no_stories":
                                st.warning("No approved stories.")
                            else:
                                st.error(f"Failed to post: {result.get('message')}")

    st.divider()
    
    # Podcast Studio
    st.markdown("## 🎙️ Global Pulse AI Podcast Studio (Beta)")
    st.info("Uses LLM logic to write a conversational radio script from your approved stories, then synthesizes an audio MP3 using Edge TTS.")
    
    with st.container(border=True):
        import os
        from backend.db.client import get_supabase
        
        edition_type = st.radio("🎙️ Select Podcast Edition", ["Morning", "Evening"], horizontal=True)
        
        col_gen1, col_gen2 = st.columns(2)
        
        with col_gen1:
            if st.button("🎙️ Write Script & Generate MP3", use_container_width=True, type="primary"):
                approved = get_approved_summaries(edition_date_str)
                if not approved:
                    st.warning("No approved stories found. Can't write a script!")
                else:
                    from backend.audio.scriptwriter import generate_podcast_script
                    from backend.audio.generator import generate_podcast_audio
                    
                    with st.spinner("✍️ Writing podcast script..."):
                        script = generate_podcast_script(approved)
                    
                    if script:
                        with st.spinner("🗣️ Synthesizing Voice (Edge TTS)..."):
                            audio_file = generate_podcast_audio(script, output_path="pulseai_daily.mp3")
                        st.rerun()

            if os.path.exists("pulseai_daily.mp3"):
                st.success("✅ Podcast Audio is Ready!")
                st.audio("pulseai_daily.mp3")
                with open("pulseai_daily.mp3", "rb") as f:
                    st.download_button("💾 Download MP3 Audio", f, file_name="pulseai_daily.mp3", mime="audio/mpeg", use_container_width=True)
                            
        with col_gen2:
            st.markdown("**🎬 YouTube Video Generator**")
            st.caption("Renders and uploads the video directly to Supabase Cloud.")
            
            if st.button("🎬 Render & Upload to Cloud", use_container_width=True):
                if not os.path.exists("pulseai_daily.mp3"):
                    st.error("You must generate the MP3 Audio first!")
                else:
                    from backend.audio.video_generator import generate_mp4_from_audio
                    with st.spinner("🎥 Rendering & Uploading Video (Takes 1 minute)..."):
                        local_mp4 = f"pulseai_video_{edition_type.lower()}.mp4"
                        video_file = generate_mp4_from_audio("pulseai_daily.mp3", output_path=local_mp4)
                        
                        # Upload to Supabase Storage
                        sb = get_supabase()
                        cloud_filename = f"{edition_date_str}_{edition_type.lower()}.mp4"
                        
                        try:
                            # Remove old file if rewriting same day/edition
                            sb.storage.from_("podcasts").remove([cloud_filename])
                        except:
                            pass
                            
                        with open(video_file, "rb") as f:
                            sb.storage.from_("podcasts").upload(
                                path=cloud_filename,
                                file=f,
                                file_options={"content-type": "video/mp4"}
                            )
                        st.rerun()
            
            cloud_filename = f"{edition_date_str}_{edition_type.lower()}.mp4"
            local_exists = os.path.exists(f"pulseai_video_{edition_type.lower()}.mp4")
            
            if local_exists:
                st.success(f"✅ {edition_type} Video Cloud Uploaded!")
                st.video(f"pulseai_video_{edition_type.lower()}.mp4")

st.markdown("— OR —")

if "linkedin_draft" not in st.session_state:
    st.session_state.linkedin_draft = ""
if "filtered_stories" not in st.session_state:
    st.session_state.filtered_stories = []

if st.button("✍️ Ghostwrite Viral LinkedIn Post", use_container_width=True):
    approved = get_approved_summaries(edition_date_str)
    if not approved:
        st.warning("No approved stories yet. Approve some stories first!")
    else:
        # Execute Evening/Morning Routing Logic
        MORNING_CATEGORIES = ['LLMs & Foundation Models', 'AI Tools & Products', 'AI in Healthcare', 'Research & Papers', 'India AI']
        EVENING_CATEGORIES = ['Funding & Acquisitions', 'Market News', 'AI Policy & Ethics']
        
        filtered = []
        if edition_type == "Morning":
            filtered = [s for s in approved if s.get('category') in MORNING_CATEGORIES]
        elif edition_type == "Evening":
            filtered = [s for s in approved if s.get('category') in EVENING_CATEGORIES]
            # Evening Fallback logic exactly as User requested
            if len(filtered) == 0:
                st.info("No Finance/Political stories found today. Falling back to the rest of the Tech morning news!")
                filtered = [s for s in approved if s.get('category') in MORNING_CATEGORIES]
                
        if len(filtered) == 0:
            filtered = approved # Absolute fallback
            
        st.session_state.filtered_stories = filtered
        
        from backend.newsletter.linkedin_bot import generate_linkedin_draft
        with st.spinner("🤖 OpenRouter AI is ghostwriting your viral post..."):
            draft = generate_linkedin_draft(filtered, edition_type)
            st.session_state.linkedin_draft = draft
        st.rerun()

if st.session_state.linkedin_draft:
    # Display the drafted text in a text area so the user can freely edit it before posting!
    edited_draft = st.text_area(
        "Review & Edit Draft before posting to LinkedIn:",
        value=st.session_state.linkedin_draft,
        height=400,
    )
    
    if st.button("🚀 Approve & Auto-Post to LinkedIn", type="primary", use_container_width=True):
        from backend.newsletter.linkedin_bot import execute_linkedin_post
        with st.spinner("Transmitting safely to LinkedIn API..."):
            main_article = st.session_state.filtered_stories[0].get("articles", {}) if st.session_state.filtered_stories else {}
            resp = execute_linkedin_post(edited_draft, main_article)
            if resp.get("status") == "success":
                st.success(f"✅ Successfully viral-posted to LinkedIn! Posted to {resp.get('posted_count')} profiles.")
            else:
                st.error(f"Failed to post: {resp.get('message')}")
