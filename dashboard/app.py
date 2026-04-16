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
    page_title="PulseAI Editorial Dashboard",
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


def run_pipeline():
    """Trigger the full aggregation + summarization pipeline."""
    from backend.aggregator.fetcher import run_aggregator
    from backend.ai.summarizer import run_summarizer
    with st.spinner("🚀 Running aggregator..."):
        agg_stats = run_aggregator()
    with st.spinner("🤖 Running AI summarizer..."):
        sum_stats = run_summarizer()
    return agg_stats, sum_stats


# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚡ PulseAI")
    st.markdown("**Editorial Dashboard**")
    st.divider()

    # Edition date picker
    selected_date = st.date_input(
        "📅 Edition Date",
        value=date.today(),
        min_value=date.today() - timedelta(days=30),
        max_value=date.today(),
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
            agg_stats, sum_stats = run_pipeline()
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
    st.markdown("*Built by Nani · PulseAI 2026*")


# ─── Main Content ─────────────────────────────────────────────────────────────

st.markdown("# ⚡ PulseAI — Editorial Dashboard")
st.markdown(f"**Edition:** {selected_date.strftime('%B %d, %Y')} &nbsp;|&nbsp; Review and approve today's AI stories")

# Stats row
stats = get_stats(edition_date_str)
total = sum(stats.values())

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("📊 Total Stories", total)
with col2:
    st.metric("⏳ Pending", stats["pending"])
with col3:
    st.metric("✅ Approved", stats["approved"])
with col4:
    st.metric("✏️ Edited", stats["edited"])
with col5:
    st.metric("❌ Rejected", stats["rejected"])

st.divider()

# Load summaries
summaries = load_summaries(status_filter, edition_date_str)

if not summaries:
    st.info(
        "📭 No summaries found for this date/filter.\n\n"
        "Run the pipeline from the sidebar to fetch and summarize today's AI news."
    )
else:
    st.markdown(f"### 📋 Stories ({len(summaries)} shown)")

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

st.divider()

# Email Newsletter Blast
st.markdown("### 📧 Send Email Newsletter")
if st.button("🚀 Blast Daily Newsletter vla Resend", use_container_width=True, type="primary"):
    from backend.newsletter.resend_mailer import blast_newsletter
    with st.spinner("Dispatching emails via Resend..."):
        result = blast_newsletter()
        if result.get("status") == "success":
            st.success(f"✅ Successfully sent to {result.get('emails_sent')} active subscribers!")
        elif result.get("status") == "no_stories":
            st.warning("No approved stories for today. Approve some stories first.")
        elif result.get("status") == "no_subscribers":
            st.warning("No active email subscribers found in the database.")
        else:
            st.error(f"Failed to send: {result.get('message')}")



# LinkedIn Newsletter Export
st.markdown("### 📤 Export for LinkedIn Newsletter")

approved = get_approved_summaries(edition_date_str)
if not approved:
    st.warning("No approved stories found. Approve some stories first!")
else:
    st.info("Select the exact stories you want to feature in today's LinkedIn post:")
    selected_linkedin_ids = []
    
    with st.container(border=True):
        for s in approved:
            article = s.get('articles') or {}
            title = article.get('title', 'Unknown')
            # Checkbox for each approved story
            if st.checkbox(f"🔗 {title}", value=True, key=f"li_post_{s['id']}"):
                selected_linkedin_ids.append(s["id"])

    if st.button("🚀 Auto-Post Selected Stories to LinkedIn", use_container_width=True, type="primary"):
        if not selected_linkedin_ids:
            st.error("You must select at least one story!")
        else:
            from backend.newsletter.linkedin_bot import blast_linkedin
            with st.spinner("Posting to LinkedIn via API..."):
                result = blast_linkedin(selected_ids=selected_linkedin_ids)
                if result.get("status") == "success":
                    st.success(f"✅ Successfully posted to your LinkedIn Profile!")
                elif result.get("status") == "no_stories":
                    st.warning("No approved stories for today. Approve stories first.")
                else:
                    st.error(f"Failed to post: {result.get('message')}")

st.markdown("— OR —")

if st.button("📋 Generate Manual LinkedIn Draft", use_container_width=True):
    approved = get_approved_summaries(edition_date_str)
    if not approved:
        st.warning("No approved stories yet. Approve some stories first!")
    else:
        newsletter = f"🔥 **PulseAI Daily — {selected_date.strftime('%B %d, %Y')}**\n"
        newsletter += f"*Your daily pulse on Artificial Intelligence*\n\n"
        newsletter += "---\n\n"

        for i, s in enumerate(approved[:10], 1):  # top 10
            article = s.get("articles") or {}
            newsletter += f"**{i}. {article.get('title', 'Story')}**\n"
            newsletter += f"{s['summary_text']}\n"
            newsletter += f"🔗 [Read more]({article.get('url', '#')})\n\n"

        newsletter += "---\n"
        newsletter += "📧 Subscribe to PulseAI for daily AI updates\n"
        newsletter += "#AI #ArtificialIntelligence #PulseAI #AINews #TechNews"

        st.text_area(
            "Copy and paste this into LinkedIn:",
            value=newsletter,
            height=400,
        )
