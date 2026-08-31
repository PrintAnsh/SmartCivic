import csv
import io
from datetime import datetime
from typing import Any, Dict, List, Optional
from utils.helpers import calculate_sla_status


def generate_complaints_csv(complaints: List[Dict[str, Any]]) -> str:
    """
    Generates a structured, sanitized RFC 4180 compliant CSV string from complaint records.
    Includes all operational, geospatial, AI triage, and SLA fields.
    """
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    headers = [
        "Complaint ID",
        "Timestamp",
        "Category",
        "Severity",
        "Priority Score (0-100)",
        "Status",
        "Assigned Department",
        "Location Address",
        "Latitude",
        "Longitude",
        "AI Analyzed",
        "AI Confidence",
        "AI Reason",
        "Recommended Action",
        "SLA Target (Hours)",
        "SLA Status",
        "Resolution Timestamp",
        "Resolution Notes",
        "Has Proof Photo",
        "Duplicate Master ID"
    ]
    writer.writerow(headers)

    for c in complaints:
        sla_info = calculate_sla_status(c)
        has_proof = bool(c.get("resolution_image_path"))
        
        row = [
            c.get("complaint_id", ""),
            c.get("timestamp", ""),
            c.get("category", ""),
            c.get("severity", ""),
            c.get("priority_score", 50),
            c.get("status", "SUBMITTED"),
            c.get("assigned_department", "Unassigned"),
            c.get("location_text", ""),
            f"{c.get('latitude', ''):.6f}" if c.get("latitude") is not None else "",
            f"{c.get('longitude', ''):.6f}" if c.get("longitude") is not None else "",
            "Yes" if c.get("is_ai_analyzed") else "No",
            f"{int(float(c.get('ai_confidence')) * 100)}%" if (c.get("ai_confidence") is not None and isinstance(c.get("ai_confidence"), (int, float))) else "",
            c.get("ai_reason", ""),
            c.get("recommended_action", ""),
            c.get("sla_target_hours", 72),
            sla_info.get("sla_badge", "ON TRACK"),
            c.get("resolution_timestamp", ""),
            c.get("resolution_notes", ""),
            "Yes" if has_proof else "No",
            c.get("is_duplicate_of") or ""
        ]
        writer.writerow(row)

    return output.getvalue()


def generate_work_order_dispatch_sheet(
    complaints: List[Dict[str, Any]],
    department_filter: Optional[str] = None
) -> str:
    """
    Generates a structured, printable field work-order dispatch brief formatted in Markdown
    for municipal field operations crews.
    """
    filtered = [
        c for c in complaints
        if c.get("status") in ["SUBMITTED", "UNDER_REVIEW", "ASSIGNED", "IN_PROGRESS"]
    ]

    if department_filter and department_filter != "All Departments":
        filtered = [c for c in filtered if c.get("assigned_department") == department_filter]

    # Sort by priority score descending
    filtered.sort(key=lambda x: x.get("priority_score", 0), reverse=True)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    dept_label = department_filter if department_filter else "All Municipal Departments"

    md = [
        f"# SMARTCIVIC MUNICIPAL FIELD DISPATCH SHEET",
        f"**Generated:** {now_str} | **Department Scope:** {dept_label} | **Active Work Orders:** {len(filtered)}",
        "---",
        ""
    ]

    if not filtered:
        md.append("*No active field work orders pending for the selected department scope.*")
        return "\n".join(md)

    for i, c in enumerate(filtered, 1):
        cid = c.get("complaint_id", "N/A")
        cat = c.get("category", "General")
        sev = c.get("severity", "Medium")
        prio = c.get("priority_score", 50)
        loc = c.get("location_text", "Address not specified")
        lat = c.get("latitude")
        lon = c.get("longitude")
        action = c.get("recommended_action", "Inspect and mitigate.")
        desc = c.get("description", "No citizen description.")
        sla_info = calculate_sla_status(c)

        coords_str = f"({lat:.6f}, {lon:.6f})" if lat and lon else "N/A"

        md.append(f"### Work Order #{i:02d}: {cid} — {cat}")
        md.append(f"- **Priority:** {prio}/100 ({sev} Severity) | **SLA:** {sla_info.get('sla_badge')}")
        md.append(f"- **Location:** {loc} `GPS: {coords_str}`")
        md.append(f"- **Citizen Description:** {desc}")
        md.append(f"- **Recommended Municipal Action:** {action}")
        md.append(f"- **Assigned Unit:** {c.get('assigned_department', 'Unassigned')}")
        md.append("")
        md.append("```")
        md.append("[ ] Field Squad Dispatched    [ ] Work Executed    [ ] Proof Photo Captured    [ ] Sign-off")
        md.append("Crew Lead Signature: ______________________   Date/Time: ______________________")
        md.append("```")
        md.append("---")
        md.append("")

    return "\n".join(md)
