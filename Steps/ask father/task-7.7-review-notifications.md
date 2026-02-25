# Task 7.7: Review Notifications (Email via Resend)

> **Phase:** 07 - Ask Father
> **Depends on:** Task 7.1 (review queue populated), Resend API key configured
> **Agent reads:** CLAUDE.md → Tech Stack (Resend for email)
> **Time estimate:** 15 minutes

---

## Objective

Send an email notification to the senior CA when new items are added to the review queue. This ensures timely reviews so CMA generation isn't blocked.

---

## What to Do

### Create File
`backend/app/services/notifications/email_service.py`

### Resend Integration

Use Resend (resend.com) API for transactional emails:
```python
import resend
resend.api_key = os.getenv("RESEND_API_KEY")
```

### Notification Triggers

**1. Review Items Created**
After classification creates review queue items, send ONE email summarizing all pending items:

Subject: `CMA AutoFill: 8 items need your review — Mehta Computers 2024-25`

Body (HTML):
```
Hi {ca_name},

{project_name} has completed AI classification. 8 items need your review before the CMA can be generated.

Summary:
- 3 items with confidence 50-70% (probably correct, just confirm)
- 5 items with confidence below 50% (need your expertise)

Top items needing review:
1. Computer Repairs Expense (₹25,000) — AI suggests: Miscellaneous Expenses (45% confidence)
2. Telephone Charges (₹12,000) — AI suggests: Communication Expenses (55% confidence)
3. ...

[Review Now →] {app_url}/projects/{project_id}/review

---
CMA AutoFill • Automated CMA Document Preparation
```

**2. All Reviews Complete**
When last review item is resolved, notify that CMA is ready to generate:

Subject: `CMA AutoFill: Mehta Computers 2024-25 — Ready to generate!`

### Email Service Functions

- `send_review_notification(firm_id, project_id, review_items)` — sends review needed email
- `send_ready_notification(firm_id, project_id)` — sends ready to generate email
- `send_email(to, subject, html_body)` — low-level Resend wrapper

### Who Receives Notifications

- All users in the firm with role 'owner' or 'ca'
- Email addresses from the `users` table
- Respect a `notification_preferences` field (future: opt-out)

### Rate Limiting

- Max 1 notification per project per hour (don't spam if re-classification runs)
- Track last notification time in project metadata

---

## What NOT to Do

- Don't send notifications for every individual review item (batch into one email)
- Don't send to 'staff' role users (only owners and CAs)
- Don't block the pipeline if email fails (log error, continue)
- Don't include sensitive financial data in email body (just item names and counts)

---

## Verification

- [ ] Classification creates review items → email sent to CA
- [ ] Email has correct project name, item count, top items
- [ ] "Review Now" link points to correct URL
- [ ] All reviews resolved → "Ready to generate" email sent
- [ ] Email failure → logged but doesn't crash pipeline
- [ ] Rate limit: re-classifying within 1 hour → no duplicate email
- [ ] Resend dashboard shows sent emails

---

## Phase 07 Complete! 🎉

All 7 tasks done. You now have:
- ✅ Review queue list with filters and sorting
- ✅ Single + bulk resolve with precedent creation
- ✅ CA decisions applied back to classification data
- ✅ Precedent CRUD (view, edit, delete)
- ✅ Learning metrics tracking improvement over time
- ✅ Email notifications for review needed / ready to generate
- ✅ Complete learning loop: AI classifies → CA corrects → precedent created → AI improves

**Next → Phase 08: Pipeline Orchestrator**
