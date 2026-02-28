"""
Learning loop metrics service.

Tracks classification accuracy trends, source breakdown, AI override rates,
review turnaround times, and cost savings.
"""

import logging
from typing import Dict, Any, Tuple
from app.db.supabase_client import get_supabase
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

# Firm-scoped cache: {firm_id: (timestamp, metrics_dict)}
_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
_CACHE_TTL = 3600  # seconds


def get_learning_metrics(firm_id: str) -> Dict[str, Any]:
    """Return learning-loop analytics for a single firm."""
    now = datetime.now().timestamp()

    # Check firm-scoped cache
    if firm_id in _cache:
        cached_time, cached_data = _cache[firm_id]
        if now - cached_time < _CACHE_TTL:
            return cached_data

    db = get_supabase()

    # ── Precedents metrics ────────────────────────────────────────────────
    prec_res = (
        db.table("classification_precedents")
        .select("created_at")
        .eq("firm_id", firm_id)
        .execute()
    )
    total_prec = len(prec_res.data)

    current_month_str = datetime.now().strftime("%Y-%m")
    this_month_prec = sum(
        1 for p in prec_res.data
        if p.get("created_at", "").startswith(current_month_str)
    )

    # ── Classification accuracy from completed projects ───────────────────
    proj_res = (
        db.table("cma_projects")
        .select("id, classification_data, updated_at")
        .eq("firm_id", firm_id)
        .eq("status", "completed")
        .execute()
    )

    trend_dict: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0, "correct": 0, "projects": 0})
    source_breakdown = {"by_precedent": 0, "by_rule": 0, "by_ai": 0, "ca_reviewed": 0}
    ai_overrides = 0
    total_ai_calls = 0
    cost_usd_avoided = 0.0

    for p in proj_res.data:
        month = (p.get("updated_at") or "")[:7]
        if not month:
            continue
        trend_dict[month]["projects"] += 1

        class_data = p.get("classification_data") or {}
        items = class_data.get("items", [])

        for itm in items:
            trend_dict[month]["total"] += 1
            source = itm.get("source", "unclassified")

            if source == "ca_reviewed":
                ai_overrides += 1
                source_breakdown["ca_reviewed"] += 1
            else:
                trend_dict[month]["correct"] += 1
                if "precedent" in source:
                    source_breakdown["by_precedent"] += 1
                    cost_usd_avoided += 0.001
                elif "rule" in source:
                    source_breakdown["by_rule"] += 1
                elif "ai" in source:
                    source_breakdown["by_ai"] += 1
                    total_ai_calls += 1

    trend_list = []
    for m, d in sorted(trend_dict.items()):
        acc = d["correct"] / d["total"] if d["total"] > 0 else 0.0
        trend_list.append({"month": m, "accuracy": round(acc, 2), "projects": d["projects"]})

    ai_override_rate = (
        ai_overrides / (ai_overrides + total_ai_calls)
        if (ai_overrides + total_ai_calls) > 0
        else 0.0
    )

    # ── Review turnaround & top corrected items ───────────────────────────
    # Use column names that actually exist in the review_queue table
    rev_res = (
        db.table("review_queue")
        .select("created_at, resolved_at, source_item_name, resolved_sheet")
        .eq("firm_id", firm_id)
        .eq("status", "resolved")
        .execute()
    )

    top_corrected: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"count": 0, "final": ""})
    hours_list = []

    for r in rev_res.data:
        created_str = r.get("created_at")
        resolved_str = r.get("resolved_at")
        if not created_str or not resolved_str:
            continue

        try:
            created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
            resolved = datetime.fromisoformat(resolved_str.replace("Z", "+00:00"))
            hrs = (resolved - created).total_seconds() / 3600
            hours_list.append(hrs)
        except (ValueError, TypeError):
            continue

        name = r.get("source_item_name", "Unknown")
        top_corrected[name]["count"] += 1
        top_corrected[name]["final"] = r.get("resolved_sheet", "Unknown")

    avg_hours = sum(hours_list) / len(hours_list) if hours_list else 0.0
    med_hours = sorted(hours_list)[len(hours_list) // 2] if hours_list else 0.0

    top_list = [
        {"term": k, "times_corrected": v["count"], "final_mapping": v["final"]}
        for k, v in top_corrected.items()
    ]
    top_list.sort(key=lambda x: x["times_corrected"], reverse=True)

    result = {
        "total_precedents": total_prec,
        "this_month_precedents": this_month_prec,
        "classification_accuracy_trend": trend_list,
        "classification_source_breakdown": source_breakdown,
        "ai_override_rate": round(ai_override_rate, 2),
        "top_corrected_items": top_list[:5],
        "review_turnaround": {
            "avg_hours": round(avg_hours, 1),
            "median_hours": round(med_hours, 1),
        },
        "cost_savings": {
            "ai_calls_avoided_by_precedents": source_breakdown["by_precedent"],
            "estimated_savings_usd": round(cost_usd_avoided, 2),
        },
    }

    # Store in firm-scoped cache
    _cache[firm_id] = (now, result)

    return result
