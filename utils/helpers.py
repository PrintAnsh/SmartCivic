from datetime import datetime, timedelta
import random
from typing import Any, Dict, List, Optional
import streamlit as st

COMPLAINT_STATUSES = [
    "SUBMITTED",
    "UNDER_REVIEW",
    "ASSIGNED",
    "IN_PROGRESS",
    "RESOLVED",
    "REJECTED"
]

MUNICIPAL_DEPARTMENTS = [
    "Public Works Department (Roads & Bridges)",
    "Sanitation & Solid Waste Management",
    "Electrical & Streetlighting Division",
    "Water Supply & Hydro Board",
    "Drainage & Sewage Operations",
    "Public Parks & Civic Infrastructure",
    "General Municipal Administration"
]

# Municipal Turnaround SLA Targets (in Hours) by Severity Tier
SLA_TARGET_HOURS = {
    "Critical": 24,   # 1 Day Emergency Turnaround
    "High": 48,       # 2 Days Urgent Field Ops
    "Medium": 72,     # 3 Days Standard Work Order
    "Low": 168        # 7 Days Routine Civic Maintenance
}


def generate_complaint_id() -> str:
    """
    Generates a unique complaint ID using the current dynamic year.
    Format: SC-{current_year}-XXXXXX (e.g., SC-2026-483921)
    """
    current_year = datetime.now().year
    random_digits = random.randint(100000, 999999)
    return f"SC-{current_year}-{random_digits}"


def get_default_department(category: str) -> str:
    """
    Maps an issue category to its responsible municipal department.
    """
    category_dept_map = {
        "Pothole / Road Damage": "Public Works Department (Roads & Bridges)",
        "Garbage & Waste": "Sanitation & Solid Waste Management",
        "Streetlight": "Electrical & Streetlighting Division",
        "Water Leakage": "Water Supply & Hydro Board",
        "Drainage & Sewage": "Drainage & Sewage Operations",
        "Public Infrastructure": "Public Parks & Civic Infrastructure",
        "Other / Unclear": "General Municipal Administration"
    }
    return category_dept_map.get(category, "General Municipal Administration")


def calculate_sla_status(record: Dict[str, Any], current_time: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Calculates dynamic SLA progress, countdown, and breach status for a complaint.
    Returns:
        {
            "target_hours": int,
            "deadline_str": str,
            "elapsed_hours": float,
            "remaining_hours": float,
            "is_breached": bool,
            "is_nearing_breach": bool,
            "sla_badge": str,
            "sla_color": str
        }
    """
    if current_time is None:
        current_time = datetime.now()

    sev = record.get("severity", "Medium")
    target_hours = record.get("sla_target_hours") or SLA_TARGET_HOURS.get(sev, 72)
    time_str = record.get("timestamp")

    try:
        logged_dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    except Exception:
        logged_dt = current_time

    deadline_dt = logged_dt + timedelta(hours=target_hours)
    deadline_str = deadline_dt.strftime("%Y-%m-%d %H:%M:%S")

    # If resolved, compute against resolution timestamp
    status = record.get("status", "SUBMITTED")
    if status == "RESOLVED":
        res_time_str = record.get("resolution_timestamp")
        try:
            resolved_dt = datetime.strptime(res_time_str, "%Y-%m-%d %H:%M:%S") if res_time_str else current_time
        except Exception:
            resolved_dt = current_time

        elapsed_hours = round((resolved_dt - logged_dt).total_seconds() / 3600.0, 1)
        on_time = resolved_dt <= deadline_dt

        return {
            "target_hours": target_hours,
            "deadline_str": deadline_str,
            "elapsed_hours": max(0.0, elapsed_hours),
            "remaining_hours": 0.0,
            "is_breached": not on_time,
            "is_nearing_breach": False,
            "sla_badge": "RESOLVED ON TIME" if on_time else "RESOLVED OVERDUE",
            "sla_color": "#10B981" if on_time else "#F59E0B"
        }

    # If active / in-progress
    elapsed_hours = round((current_time - logged_dt).total_seconds() / 3600.0, 1)
    remaining_hours = round((deadline_dt - current_time).total_seconds() / 3600.0, 1)
    is_breached = current_time > deadline_dt
    is_nearing_breach = (not is_breached) and (remaining_hours <= max(4.0, target_hours * 0.25))

    if is_breached:
        badge = f"SLA BREACHED (+{abs(remaining_hours):.0f}h)"
        color = "#EF4444"
    elif is_nearing_breach:
        badge = f"SLA EXPIRING ({remaining_hours:.0f}h left)"
        color = "#F59E0B"
    else:
        badge = f"SLA ON TRACK ({remaining_hours:.0f}h left)"
        color = "#10B981"

    return {
        "target_hours": target_hours,
        "deadline_str": deadline_str,
        "elapsed_hours": max(0.0, elapsed_hours),
        "remaining_hours": remaining_hours,
        "is_breached": is_breached,
        "is_nearing_breach": is_nearing_breach,
        "sla_badge": badge,
        "sla_color": color
    }


def create_complaint_record(
    category: str,
    description: str,
    location_text: str,
    latitude: float = None,
    longitude: float = None,
    image_file=None,
    ai_category: str = None,
    ai_confidence: float = None,
    ai_confidence_level: str = None,
    ai_reason: str = None,
    ai_summary: str = None,
    severity: str = None,
    priority_score: int = None,
    risk_factors: list = None,
    recommended_action: str = None,
    status: str = "SUBMITTED",
    assigned_department: str = None,
    is_duplicate_of: str = None
) -> dict:
    """
    Creates a structured complaint record dictionary.
    Stores separate human-readable location_text, numeric GPS coordinates, image evidence,
    unified AI classification, severity, priority, risk factors, recommended action,
    SLA turnaround targets, resolution proof paths, and duplicate tracking.
    """
    complaint_id = generate_complaint_id()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    final_cat = category if category != "Select category" else "Uncategorized"
    dept = assigned_department or get_default_department(final_cat)
    sev = severity or "Medium"
    sla_target = SLA_TARGET_HOURS.get(sev, 72)

    record = {
        "complaint_id": complaint_id,
        "timestamp": timestamp,
        "category": final_cat,
        "final_category": final_cat,
        "ai_category": ai_category,
        "ai_confidence": ai_confidence,
        "ai_confidence_level": ai_confidence_level,
        "ai_reason": ai_reason,
        "ai_summary": ai_summary,
        "is_ai_analyzed": ai_category is not None,
        "severity": sev,
        "priority_score": priority_score if priority_score is not None else 50,
        "risk_factors": risk_factors if isinstance(risk_factors, list) else [],
        "recommended_action": recommended_action or "",
        "description": description.strip(),
        "location_text": location_text.strip(),
        "latitude": latitude,
        "longitude": longitude,
        "image": image_file,
        "image_path": None,
        "status": status,
        "assigned_department": dept,
        "resolution_notes": "",
        "resolution_image": None,
        "resolution_image_path": None,
        "resolution_timestamp": None,
        "sla_target_hours": sla_target,
        "is_duplicate_of": is_duplicate_of,
        "duplicate_count": 0,
        "status_history": [
            {
                "status": status,
                "timestamp": timestamp,
                "note": "Citizen complaint logged via SmartCivic."
            }
        ]
    }

    return record


def init_session_state():
    """
    Initializes unified session state variables for complaint tracking, location, forms, and AI.
    Loads persistent complaints from data/complaints.json into session state.
    """
    try:
        from utils.storage import load_all_complaints
        persisted_complaints = load_all_complaints()
    except Exception as e:
        print(f"[SmartCivic Helpers] Could not load persisted complaints: {e}")
        persisted_complaints = []

    if "complaints" not in st.session_state or not st.session_state["complaints"]:
        st.session_state["complaints"] = persisted_complaints

    if "submitted_complaint" not in st.session_state:
        st.session_state["submitted_complaint"] = None

    if "selected_category" not in st.session_state:
        st.session_state["selected_category"] = "Select category"

    if "page" not in st.session_state:
        st.session_state["page"] = "Home"

    # Single Source of Truth for GPS coordinates and Location
    if "gps_latitude" not in st.session_state:
        st.session_state["gps_latitude"] = None

    if "gps_longitude" not in st.session_state:
        st.session_state["gps_longitude"] = None

    if "location_text" not in st.session_state:
        st.session_state["location_text"] = ""

    if "loc_key_counter" not in st.session_state:
        st.session_state["loc_key_counter"] = 0

    if "autofill_status" not in st.session_state:
        st.session_state["autofill_status"] = None

    # AI Classification & Risk Assessment State
    if "ai_result" not in st.session_state:
        st.session_state["ai_result"] = None

    if "ai_status" not in st.session_state:
        st.session_state["ai_status"] = "idle"

    if "ai_severity" not in st.session_state:
        st.session_state["ai_severity"] = None

    if "ai_priority_score" not in st.session_state:
        st.session_state["ai_priority_score"] = None

    if "ai_risk_factors" not in st.session_state:
        st.session_state["ai_risk_factors"] = None

    if "ai_recommended_action" not in st.session_state:
        st.session_state["ai_recommended_action"] = None

    if "photo_mode" not in st.session_state:
        st.session_state["photo_mode"] = "Take a Photo"

    # Search and Filter state for Track and Triage
    if "track_search_id" not in st.session_state:
        st.session_state["track_search_id"] = ""

    if "triage_filter_status" not in st.session_state:
        st.session_state["triage_filter_status"] = "All"

    if "triage_filter_severity" not in st.session_state:
        st.session_state["triage_filter_severity"] = "All"

    # v0.5 Map & Duplicate State
    if "map_selected_cid" not in st.session_state:
        st.session_state["map_selected_cid"] = None

    if "potential_duplicate_match" not in st.session_state:
        st.session_state["potential_duplicate_match"] = None
