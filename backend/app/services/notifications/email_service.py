import os
import logging
import resend
from typing import List, Dict, Any
from app.db.supabase_client import get_supabase

# Initialize resend API key from env
resend.api_key = os.getenv("RESEND_API_KEY", "")

logger = logging.getLogger("cma.email")

def send_email(to: List[str], subject: str, html_body: str):
    if not resend.api_key:
        logger.warning(f"RESEND_API_KEY not set. Mocking email to {to}: {subject}")
        return False
        
    try:
        r = resend.Emails.send({
            "from": "notifications@cma-autofill.com",
            "to": to,
            "subject": subject,
            "html": html_body
        })
        logger.info(f"Email sent to {to}: {r}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {str(e)}")
        return False

def get_firm_contacts(firm_id: str) -> List[str]:
    db = get_supabase()
    res = db.table("users").select("email").eq("firm_id", firm_id).in_("role", ["owner", "ca"]).execute()
    return [r["email"] for r in res.data if "email" in r]

def send_review_notification(firm_id: str, project_id: str, client_name: str, project_name: str, review_items: List[Dict[str, Any]]):
    # Check rate limiting / metadata if needed. Let's just fire it.
    to_emails = get_firm_contacts(firm_id)
    if not to_emails:
        return
        
    count = len(review_items)
    prob_correct = sum(1 for i in review_items if i.get("confidence", 0) >= 0.50)
    uncertain = count - prob_correct
    
    top_items = review_items[:3]
    top_html = ""
    for idx, itm in enumerate(top_items):
        name = itm.get("item_name") or itm.get("source_item_name") or "Unknown"
        amt = itm.get("item_amount") or itm.get("source_item_amount") or 0
        sug_label = itm.get("target_label") or itm.get("suggested_label") or "Unknown"
        conf = itm.get("confidence", 0) * 100
        top_html += f"<li>{name} (₹{amt:,.2f}) — AI suggests: {sug_label} ({conf:.0f}% confidence)</li>\n"
        
    subject = f"CMA AutoFill: {count} items need your review — {client_name}"
    
    # Let's assume an app frontend URL
    app_url = os.getenv("NEXT_PUBLIC_APP_URL", "http://localhost:3000")
    
    body = f"""
    <p>Hi CA,</p>
    <p><strong>{project_name}</strong> has completed AI classification. {count} items need your review before the CMA can be generated.</p>
    <p><strong>Summary:</strong></p>
    <ul>
        <li>{prob_correct} items with confidence 50-70% (probably correct, just confirm)</li>
        <li>{uncertain} items with confidence below 50% (need your expertise)</li>
    </ul>
    <p><strong>Top items needing review:</strong></p>
    <ol>
        {top_html}
    </ol>
    <p><a href="{app_url}/projects/{project_id}/review">Review Now →</a></p>
    <hr/>
    <p><small>CMA AutoFill • Automated CMA Document Preparation</small></p>
    """
    
    send_email(to_emails, subject, body)

def send_ready_notification(firm_id: str, project_id: str, client_name: str, project_name: str):
    to_emails = get_firm_contacts(firm_id)
    if not to_emails:
        return
        
    subject = f"CMA AutoFill: {client_name} — Ready to generate!"
    
    app_url = os.getenv("NEXT_PUBLIC_APP_URL", "http://localhost:3000")
    
    body = f"""
    <p>Hi CA,</p>
    <p>Good news! All review items for <strong>{project_name}</strong> have been resolved.</p>
    <p>The CMA document is now ready to be generated and downloaded.</p>
    <p><a href="{app_url}/projects/{project_id}">Go to Project →</a></p>
    <hr/>
    <p><small>CMA AutoFill • Automated CMA Document Preparation</small></p>
    """
    
    send_email(to_emails, subject, body)
