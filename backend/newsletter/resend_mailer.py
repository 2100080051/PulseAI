import os
import sys
import resend
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.db.client import get_supabase
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.environ.get("RESEND_API_KEY")

def generate_newsletter_html(stories):
    date_str = date.today().strftime("%B %d, %Y")
    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #050917; color: #f1f5f9; padding: 30px 15px; text-align: center;">
        <div style="max-width: 600px; margin: 0 auto; background: #0d1224; border: 1px solid #1e293b; border-radius: 12px; overflow: hidden; text-align: left;">
            <div style="padding: 30px; text-align: center; border-bottom: 1px solid #1e293b;">
                <h1 style="color: #fff; margin: 0; font-size: 24px;">Pulse<span style="color: #6366f1;">AI</span></h1>
                <p style="color: #94a3b8; font-size: 14px; margin: 10px 0 0 0;">Your daily pulse on Artificial Intelligence</p>
                <p style="color: #6366f1; font-size: 12px; font-weight: bold; margin: 10px 0 0 0; text-transform: uppercase; letter-spacing: 1px;">{date_str}</p>
            </div>
            <div style="padding: 30px;">
    """
    
    for idx, s in enumerate(stories):
        article = s.get('articles') or {}
        title = article.get('title', 'AI Story')
        url = article.get('url', '#')
        summary = s.get('summary_text', '')
        category = s.get('category', 'AI News')
        
        html += f"""
                <div style="margin-bottom: 30px; padding-bottom: {'30px' if idx < len(stories)-1 else '0'}; border-bottom: {'1px solid #1e293b' if idx < len(stories)-1 else '0'};">
                    <span style="display: inline-block; padding: 4px 10px; background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.2); color: #8b5cf6; border-radius: 100px; font-size: 11px; font-weight: bold; text-transform: uppercase; margin-bottom: 10px;">{category}</span>
                    <h2 style="font-size: 18px; margin: 0 0 12px 0; line-height: 1.4;"><a href="{url}" style="color: #fff; text-decoration: none;">{title}</a></h2>
                    <p style="color: #cbd5e1; font-size: 15px; line-height: 1.6; margin: 0 0 15px 0;">{summary}</p>
                    <a href="{url}" style="color: #6366f1; text-decoration: none; font-size: 14px; font-weight: bold;">Read article &rarr;</a>
                </div>
        """
        
    html += """
            </div>
            <div style="padding: 20px; background: #0a0e1b; text-align: center; border-top: 1px solid #1e293b;">
                <p style="color: #475569; font-size: 12px; margin: 0;">You are receiving this because you subscribed to PulseAI.</p>
                <p style="color: #475569; font-size: 12px; margin: 5px 0 0 0;">&copy; PulseAI 2026. All rights reserved.</p>
            </div>
        </div>
    </div>
    """
    return html

def blast_newsletter():
    """Send out the newsletter using Resend."""
    if not resend.api_key:
        return {"status": "error", "message": "RESEND_API_KEY not found in environment."}
        
    sb = get_supabase()
    
    # Fetch active subscribers
    subs_res = sb.table("subscribers").select("email").eq("is_active", True).execute()
    emails = [s['email'] for s in subs_res.data]
    
    if not emails:
        return {"status": "no_subscribers", "message": "No active subscribers found."}
        
    # Fetch top 10 recent approved stories
    stories_res = (sb.table("summaries")
               .select("*, articles(title, url)")
               .in_("status", ["approved", "edited"])
               .order("created_at", desc=True)
               .limit(10)
               .execute())
               
    stories = stories_res.data
    if not stories:
        return {"status": "no_stories", "message": "No approved stories to send."}
        
    html_content = generate_newsletter_html(stories)
    
    try:
        # Note: on free Resend tier without domain verification, you can only send to your own verified email.
        # We will use 'onboarding@resend.dev' as the from address to ensure it works.
        response = resend.Emails.send({
            "from": "PulseAI <onboarding@resend.dev>",
            "to": emails,
            "subject": f"PulseAI Daily: {len(stories)} Top AI Stories",
            "html": html_content
        })
        return {"status": "success", "emails_sent": len(emails), "resend_id": response.get('id', '')}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    result = blast_newsletter()
    print("Newsletter Dispatch Result:", result)
