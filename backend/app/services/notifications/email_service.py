"""
Email notification service using Resend.

Sends notifications when:
- Review items need CA attention
- Pipeline completes and CMA is ready to download
"""

import os
import logging
from typing import List, Dict, Any

import resend

from app.db.supabase_client import get_supabase

logger = logging.getLogger("cma.email")


def _get_api_key() -> str:
    """Read API key at call time so env changes are picked up."""
    return os.getenv("RESEND_API_KEY", "")


def send_email(to: List[str], subject: str, html_body: str) -> bool:
    """Send an email via Resend. Returns True on success."""
    api_key = _get_api_key()
    if not api_key:
        logger.warning("RESEND_API_KEY not set. Skipping email to %s: %s", to, subject)
        return False

    resend.api_key = api_key

    try:
        r = resend.Emails.send({
            "from": "notifications@cma-autofill.com",
            "to": to,
            "subject": subject,
            "html": html_body,
        })
        logger.info("Email sent to %s: %s", to, r)
        return True
    except Exception as e:
        logger.error("Failed to send email to %s: %s", to, e)
        return False


def get_firm_contacts(firm_id: str) -> List[str]:
    """Get email addresses for owners and CAs in the firm."""
    db = get_supabase()
    res = (
        db.table("users")
        .select("email")
        .eq("firm_id", firm_id)
        .in_("role", ["owner", "ca"])
        .execute()
    )
    return [r["email"] for r in res.data if r.get("email")]


def send_review_notification(
    firm_id: str,
    project_id: str,
    client_name: str,
    project_name: str,
    review_items: List[Dict[str, Any]],
) -> None:
    """Send email notifying CAs that items need review."""
    to_emails = get_firm_contacts(firm_id)
    if not to_emails:
        return

    count = len(review_items)
    prob_correct = sum(1 for i in review_items if (i.get("confidence") or 0) >= 0.50)
    uncertain = count - prob_correct

    top_items = review_items[:3]
    top_html = ""
    for itm in top_items:
        name = itm.get("item_name") or itm.get("source_item_name") or "Unknown"
        amt = itm.get("item_amount") or itm.get("source_item_amount") or 0
        sug_label = itm.get("target_label") or itm.get("suggested_label") or "Unknown"
        conf = (itm.get("confidence") or 0) * 100
        top_html += f"<li>{name} (₹{amt:,.2f}) — AI suggests: {sug_label} ({conf:.0f}% confidence)</li>\n"

    subject = f"CMA AutoFill: {count} items need your review — {client_name}"

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


def send_ready_notification(
    firm_id: str,
    project_id: str,
    client_name: str,
    project_name: str,
) -> None:
    """Send email notifying CAs that the CMA is ready to download."""
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
