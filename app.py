from datetime import datetime
import os
from pathlib import Path
import streamlit as st
from PIL import Image

from ai import CIVIC_CATEGORIES, analyze_civic_issue
from components.map_view import render_gis_map_component
from components.ui_components import inject_custom_css
from utils.export import (
    generate_complaints_csv,
    generate_work_order_dispatch_sheet
)
from utils.helpers import (
    COMPLAINT_STATUSES,
    MUNICIPAL_DEPARTMENTS,
    calculate_sla_status,
    create_complaint_record,
    init_session_state,
)
from utils.location import (
    find_nearby_potential_duplicates,
    render_geolocation_component,
    reverse_geocode,
)
from utils.storage import (
    PROJECT_ROOT,
    compute_municipal_analytics,
    get_complaint_by_id,
    link_duplicate_complaint,
    load_all_complaints,
    save_complaint,
    update_complaint_status,
)

# Page configuration
st.set_page_config(
    page_title="SmartCivic — Smart Civic Technology",
    page_icon="▪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject minimal editorial dark design tokens
inject_custom_css()

# Initialize session state storage
init_session_state()

# Single Source of Truth for GPS Query Param Handling
if "geo_lat" in st.query_params and "geo_lon" in st.query_params:
    try:
        lat = float(st.query_params.get("geo_lat"))
        lon = float(st.query_params.get("geo_lon"))
        st.session_state["gps_latitude"] = lat
        st.session_state["gps_longitude"] = lon
        print(f"\n[SmartCivic State Sync] GPS Coordinates Received: ({lat}, {lon})")
    except Exception as e:
        print(f"[SmartCivic GPS Query Param Error] {e}")


def set_page(page_name: str, preselected_category: str = None):
    """
    Helper to update page state and preselect category if provided.
    """
    st.session_state["page"] = page_name
    if preselected_category:
        st.session_state["selected_category"] = preselected_category
    st.rerun()


def render_top_navigation():
    """
    Renders an interactive minimal editorial top navigation bar with v0.5 GIS Map.
    """
    nav_col1, nav_col2, nav_col3, nav_col4, nav_col5, nav_col6, nav_col7 = st.columns(
        [2.2, 0.9, 1.4, 0.9, 1.1, 1.7, 0.9],
        gap="small"
    )

    current = st.session_state.get("page", "Home")

    with nav_col1:
        st.markdown(
            """<div class="nav-logo">
<span class="nav-logo-dot"></span>
<span>SMARTCIVIC</span>
</div>""",
            unsafe_allow_html=True
        )

    with nav_col2:
        btn_type = "primary" if current == "Home" else "secondary"
        if st.button("Home", key="nav_btn_home", type=btn_type, use_container_width=True):
            set_page("Home")

    with nav_col3:
        btn_type = "primary" if current == "Report an Issue" else "secondary"
        if st.button("Report an Issue", key="nav_btn_report", type=btn_type, use_container_width=True):
            set_page("Report an Issue")

    with nav_col4:
        btn_type = "primary" if current == "Track" else "secondary"
        if st.button("Track", key="nav_btn_track", type=btn_type, use_container_width=True):
            set_page("Track")

    with nav_col5:
        btn_type = "primary" if current == "GIS Map" else "secondary"
        if st.button("GIS Map", key="nav_btn_map", type=btn_type, use_container_width=True):
            set_page("GIS Map")

    with nav_col6:
        btn_type = "primary" if current == "Analytics & Triage" else "secondary"
        if st.button("Analytics & Triage", key="nav_btn_analytics", type=btn_type, use_container_width=True):
            set_page("Analytics & Triage")

    with nav_col7:
        btn_type = "primary" if current == "About" else "secondary"
        if st.button("About", key="nav_btn_about", type=btn_type, use_container_width=True):
            set_page("About")

    st.markdown("<hr style='border: none; border-top: 1px solid #1A1A1A; margin: 1rem 0 2.5rem 0;'>", unsafe_allow_html=True)


def render_home():
    """
    Renders the Home page with hero visual and interactive issue categories.
    """
    col_hero_text, col_hero_diagram = st.columns([1.1, 0.9], gap="large")

    with col_hero_text:
        st.markdown(
            """<div class="eyebrow">
<span>▪</span> SMART CIVIC TECHNOLOGY · v0.5 MUNICIPAL RELEASE
</div>
<div class="headline-hero">
Make Your City<br>Better.
</div>
<div class="headline-sub">
One report can start a change.
</div>
<div class="desc-editorial">
See a problem? Capture it. SmartCivic uses multimodal AI vision to classify civic issues automatically, 
evaluates risk and severity, eliminates duplicate tickets via proximity clustering, and tracks transparent municipal resolution.
</div>""",
            unsafe_allow_html=True
        )

        c_btn1, c_btn2 = st.columns([1.3, 1], gap="medium")
        with c_btn1:
            if st.button("Report an Issue →", key="hero_primary_cta", type="primary", use_container_width=True):
                set_page("Report an Issue")
        with c_btn2:
            if st.button("Explore GIS Map 🗺️", key="hero_secondary_cta", type="secondary", use_container_width=True):
                set_page("GIS Map")

    with col_hero_diagram:
        diagram_html = """<div class="diagram-container">
<div class="diagram-eyebrow">SYSTEM ARCHITECTURE FLOW</div>
<div class="diagram-node active">
<div>
<div class="diagram-node-title">01 — CITIZEN INTAKE</div>
<div class="diagram-node-sub">Live camera capture + GPS geocoding</div>
</div>
<div class="diagram-badge">INTAKE</div>
</div>
<div class="diagram-arrow">↓</div>
<div class="diagram-node active">
<div>
<div class="diagram-node-title">02 — MULTIMODAL AI TRIAGE</div>
<div class="diagram-node-sub">Gemini Vision Category, Severity & Risk</div>
</div>
<div class="diagram-badge active-ai">GEMINI AI</div>
</div>
<div class="diagram-arrow">↓</div>
<div class="diagram-node active">
<div>
<div class="diagram-node-title">03 — GEOSPATIAL INTELLIGENCE</div>
<div class="diagram-node-sub">Proximity Duplicate Clustering & GIS Mapping</div>
</div>
<div class="diagram-badge" style="background: rgba(96, 165, 250, 0.15); color: #60A5FA; border: 1px solid rgba(96, 165, 250, 0.3);">GIS ACTIVE</div>
</div>
<div class="diagram-arrow">↓</div>
<div class="diagram-node active">
<div>
<div class="diagram-node-title">04 — MUNICIPAL DISPATCH & SLA</div>
<div class="diagram-node-sub">Priority Queue, SLA Timers & Resolution Proof</div>
</div>
<div class="diagram-badge" style="background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3);">OPERATIONAL</div>
</div>
</div>"""
        st.markdown(diagram_html, unsafe_allow_html=True)

    # Section: The Problem & Interactive Issue Categories
    st.markdown("<hr class='editorial-divider'>", unsafe_allow_html=True)

    st.markdown(
        """<div class="eyebrow">THE PROBLEM</div>
<div class="section-headline">
Civic problems are everywhere.<br>Knowing where to report them shouldn't be.
</div>
<div style="font-size: 0.9rem; color: #888888; margin-bottom: 1.5rem;">
Select an issue type below to initiate a structured report:
</div>""",
        unsafe_allow_html=True
    )

    # Interactive Issue Types Grid
    cat_col1, cat_col2 = st.columns(2, gap="medium")

    with cat_col1:
        if st.button("01. Road & Potholes  →", key="cat_btn_1", type="secondary", use_container_width=True):
            set_page("Report an Issue", preselected_category="Pothole / Road Damage")
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        if st.button("02. Garbage & Waste  →", key="cat_btn_2", type="secondary", use_container_width=True):
            set_page("Report an Issue", preselected_category="Garbage & Waste")
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        if st.button("03. Streetlights  →", key="cat_btn_3", type="secondary", use_container_width=True):
            set_page("Report an Issue", preselected_category="Streetlight")

    with cat_col2:
        if st.button("04. Water & Leakage  →", key="cat_btn_4", type="secondary", use_container_width=True):
            set_page("Report an Issue", preselected_category="Water Leakage")
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        if st.button("05. Drainage & Sewage  →", key="cat_btn_5", type="secondary", use_container_width=True):
            set_page("Report an Issue", preselected_category="Drainage & Sewage")
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        if st.button("06. Public Infrastructure  →", key="cat_btn_6", type="secondary", use_container_width=True):
            set_page("Report an Issue", preselected_category="Public Infrastructure")


def render_report():
    """
    Renders the citizen issue intake form with Gemini Multimodal Vision AI triage,
    automatic duplicate proximity warnings, and persistent complaint creation.
    """
    if st.session_state.get("submitted_complaint"):
        sub = st.session_state["submitted_complaint"]
        cid = sub.get("complaint_id", "N/A")
        cat = sub.get("category", "N/A")
        loc = sub.get("location_text", "N/A")
        time_str = sub.get("timestamp", "N/A")
        dept = sub.get("assigned_department", "Public Works")
        sev = sub.get("severity", "Medium")
        prio = sub.get("priority_score", 50)
        sla_hours = sub.get("sla_target_hours", 72)
        sev_cls = f"severity-{sev.lower()}" if sev.lower() in ["low", "medium", "high", "critical"] else "severity-medium"

        st.markdown(
            f"""<div class="success-card">
<div class="success-title">✓ REPORT LOGGED PERSISTENTLY</div>
<div class="success-desc">
Your report has been assigned ID <strong>{cid}</strong> and routed to <strong>{dept}</strong>.
</div>
<div class="success-details-grid">
<div><strong>ID:</strong> <span style="font-family: monospace; color: #C45D63;">{cid}</span></div>
<div><strong>Category:</strong> {cat}</div>
<div><strong>Location:</strong> {loc}</div>
<div><strong>Logged At:</strong> {time_str}</div>
<div><strong>Severity:</strong> <span class="ai-severity-badge {sev_cls}">{sev}</span></div>
<div><strong>Priority:</strong> {prio}/100</div>
<div><strong>SLA Target:</strong> {sla_hours} Hours</div>
<div><strong>Initial Status:</strong> <span class="status-badge status-submitted">SUBMITTED</span></div>
</div>
</div>""",
            unsafe_allow_html=True
        )

        c_track_btn, c_new_btn = st.columns([1, 1], gap="medium")
        with c_track_btn:
            if st.button("Track Your Ticket →", key="btn_goto_track", type="primary", use_container_width=True):
                st.session_state["submitted_complaint"] = None
                set_page("Track")
        with c_new_btn:
            if st.button("Submit Another Report", key="btn_reset_report", type="secondary", use_container_width=True):
                st.session_state["submitted_complaint"] = None
                st.session_state["ai_result"] = None
                st.session_state["ai_status"] = "idle"
                st.session_state["gps_latitude"] = None
                st.session_state["gps_longitude"] = None
                st.session_state["location_text"] = ""
                st.rerun()
        return

    st.markdown(
        """<div class="eyebrow">CITIZEN REPORTING INTAKE</div>
<div class="headline-hero" style="font-size: 2.8rem; margin-bottom: 0.5rem;">
Report a Civic Issue.
</div>
<div class="headline-sub" style="font-size: 1.15rem; color: #888888; margin-bottom: 2.5rem;">
Capture a photo, let AI classify and triage the problem, and verify location for municipal dispatch.
</div>""",
        unsafe_allow_html=True
    )

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='form-label-custom'>01. VISUAL EVIDENCE *</div>", unsafe_allow_html=True)
        photo_mode = st.radio(
            "Photo input method",
            options=["Take a Photo", "Upload an Image"],
            horizontal=True,
            label_visibility="collapsed",
            key="photo_mode_radio"
        )

        final_image = None
        if photo_mode == "Take a Photo":
            camera_file = st.camera_input("Take a photo of the issue", key="camera_input")
            if camera_file is not None:
                final_image = camera_file
        else:
            upload_file = st.file_uploader("Upload an image (JPG, PNG)", type=["jpg", "jpeg", "png"], key="file_upload_input")
            if upload_file is not None:
                final_image = upload_file

        if final_image is not None:
            if st.session_state.get("ai_status") == "idle" or st.session_state.get("ai_result") is None:
                with st.spinner("🤖 Multimodal Gemini Vision analyzing issue & assessing risk..."):
                    try:
                        pil_img = Image.open(final_image)
                        ai_res = analyze_civic_issue(pil_img)
                        st.session_state["ai_result"] = ai_res
                        st.session_state["ai_status"] = "completed"
                        if ai_res.get("success") and ai_res.get("category"):
                            st.session_state["selected_category"] = ai_res.get("category")
                            st.session_state["ai_severity"] = ai_res.get("severity")
                            st.session_state["ai_priority_score"] = ai_res.get("priority_score")
                            st.session_state["ai_risk_factors"] = ai_res.get("risk_factors")
                            st.session_state["ai_recommended_action"] = ai_res.get("recommended_action")
                    except Exception as e:
                        import re
                        # Sanitize any potential API keys/tokens (long alphanumeric strings)
                        safe_e = re.sub(r'[A-Za-z0-9_-]{35,}', '[REDACTED_TOKEN]', str(e))
                        print(f"AI Exception: {type(e).__name__} - {safe_e}", flush=True)
                        st.session_state["ai_status"] = "error"
                        st.session_state["ai_result"] = {
                            "success": False,
                            "error": str(e),
                            "message": "AI analysis is temporarily unavailable."
                        }

        # AI Breakdown Card / Fallback State
        ai_res = st.session_state.get("ai_result")
        if ai_res and ai_res.get("success"):
            cat = ai_res.get("category")
            conf_str = ai_res.get("confidence_percentage", "90%")
            sev = ai_res.get("severity", "Medium")
            prio = ai_res.get("priority_score", 50)
            sev_cls = f"severity-{sev.lower()}" if sev.lower() in ["low", "medium", "high", "critical"] else "severity-medium"
            risks_html = "".join([f"<li>{r}</li>" for r in ai_res.get("risk_factors", [])])

            st.markdown(
                f"""<div class="ai-assessment-card">
<div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.5rem;">
<span class="ai-title">🤖 AI MULTIMODAL TRIAGE</span>
<span class="ai-confidence-badge">{conf_str} Confidence</span>
</div>
<div style="font-size: 1.15rem; font-weight: 700; color: #FFF; margin-bottom: 0.4rem;">{cat}</div>
<div style="margin-bottom: 0.8rem;">
<span class="ai-severity-badge {sev_cls}">{sev} SEVERITY</span>
<span style="font-family: monospace; color: #E5E5E5; margin-left: 8px; font-weight: 700;">Priority Score: {prio}/100</span>
</div>
<div class="ai-field-label">AI SUMMARY</div>
<div style="font-size: 0.85rem; color: #CCC; margin-bottom: 0.6rem; line-height: 1.4;">{ai_res.get('summary', 'N/A')}</div>
<div class="ai-field-label">OBSERVED RISK FACTORS</div>
<ul style="margin: 0 0 0.8rem 1.2rem; padding: 0; font-size: 0.82rem; color: #BBB;">{risks_html}</ul>
<div class="ai-field-label">RECOMMENDED ACTION</div>
<div style="font-size: 0.85rem; color: #10B981; line-height: 1.4;">{ai_res.get('recommended_action', 'N/A')}</div>
</div>""",
                unsafe_allow_html=True
            )
        elif ai_res and not ai_res.get("success"):
            user_msg = ai_res.get("message", "AI analysis is temporarily unavailable.")
            # Sanitize message to prevent leaking keys, internal codes or system traces
            if any(term in str(user_msg).lower() for term in ["key", "secret", "traceback", "clienterror", "apiexception", "404", "503", "socket", "http"]):
                user_msg = "AI multimodal vision service is temporarily unavailable."

            st.markdown(
                f"""<div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 8px; padding: 0.85rem; margin-top: 1rem;">
<div style="color: #FBBF24; font-weight: 600; font-size: 0.88rem; margin-bottom: 0.35rem;">⚠️ AI Triage Temporarily Unavailable</div>
<div style="color: #CBD5E1; font-size: 0.82rem; line-height: 1.5;">{user_msg} Please select the issue category manually on the right and continue submitting your report.</div>
</div>""",
                unsafe_allow_html=True
            )

    with col_right:
        # Category Selector
        st.markdown("<div class='form-label-custom'>02. ISSUE CATEGORY *</div>", unsafe_allow_html=True)
        options = ["Select category"] + CIVIC_CATEGORIES
        cur_cat = st.session_state.get("selected_category", "Select category")
        idx = options.index(cur_cat) if cur_cat in options else 0
        category = st.selectbox("Category", options=options, index=idx, label_visibility="collapsed", key="category_select")
        st.session_state["selected_category"] = category

        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        # Location Section
        st.markdown("<div class='form-label-custom'>03. LOCATION & COORDINATES *</div>", unsafe_allow_html=True)
        render_geolocation_component(st.session_state.get("gps_latitude"), st.session_state.get("gps_longitude"))

        # Auto-Fill Address Button
        c_lat = st.session_state.get("gps_latitude")
        c_lon = st.session_state.get("gps_longitude")
        if c_lat is not None and c_lon is not None:
            col_coords, col_autofill = st.columns([1.5, 1], gap="small")
            with col_coords:
                st.markdown(f"<div style='font-family: monospace; font-size: 0.85rem; color: #C45D63; padding-top: 6px;'>📍 {c_lat:.6f}, {c_lon:.6f}</div>", unsafe_allow_html=True)
            with col_autofill:
                if st.button("Auto-Fill Address", key="btn_autofill_addr", use_container_width=True):
                    with st.spinner("Geocoding coordinates..."):
                        addr = reverse_geocode(c_lat, c_lon)
                        if addr:
                            st.session_state["location_text"] = addr
                            st.session_state["loc_key_counter"] = st.session_state.get("loc_key_counter", 0) + 1
                            st.rerun()

        loc_text = st.text_input(
            "Address or location details",
            value=st.session_state.get("location_text", ""),
            placeholder="e.g. Near MITS Circle, Race Course Road, Gwalior",
            label_visibility="collapsed",
            key=f"loc_input_{st.session_state.get('loc_key_counter', 0)}"
        )
        st.session_state["location_text"] = loc_text

        # -------------------------------------------------------------
        # v0.5 DUPLICATE PROXIMITY DETECTION & WARNING BANNER
        # -------------------------------------------------------------
        matched_duplicate_cid = None
        if c_lat is not None and c_lon is not None and category and category != "Select category":
            nearby_matches = find_nearby_potential_duplicates(
                category=category,
                lat=c_lat,
                lon=c_lon,
                complaints=st.session_state.get("complaints", []),
                radius_meters=75.0
            )
            if nearby_matches:
                top_match = nearby_matches[0]
                matched_duplicate_cid = top_match.get("complaint_id")
                dist_m = int(top_match.get("distance_meters", 30))
                st.markdown(
                    f"""<div class="duplicate-alert-banner">
<div style="font-weight: 800; font-size: 0.8rem; color: #F59E0B; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.3rem;">
⚠️ SIMILAR ACTIVE REPORT NEARBY ({dist_m}m away)
</div>
<div style="font-size: 0.85rem; color: #DDD; line-height: 1.4;">
An active ticket for <strong>{category}</strong> is already open at this location (<span style="font-family: monospace; color: #C45D63;">{matched_duplicate_cid}</span>).
Submitting will link your report to increase municipal triage urgency.
</div>
</div>""",
                    unsafe_allow_html=True
                )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # Description Section
        st.markdown("<div class='form-label-custom'>04. CITIZEN DESCRIPTION *</div>", unsafe_allow_html=True)
        description = st.text_area(
            "Describe the problem",
            placeholder="e.g. Deep pothole near the college main gate spanning 2 meters. Scooters slipping during night hours.",
            height=90,
            label_visibility="collapsed",
            key="desc_input_field"
        )

    st.markdown("<hr style='border: none; border-top: 1px solid #1A1A1A; margin: 2rem 0;'>", unsafe_allow_html=True)

    col_empty, col_submit = st.columns([2.5, 1.5])
    with col_empty:
        st.caption("* Required fields: Visual evidence (Camera/Upload), Location, Issue description")
    with col_submit:
        submit_clicked = st.button("Submit Report →", key="submit_complaint_btn", type="primary", use_container_width=True)

    if submit_clicked:
        missing = []
        if final_image is None:
            missing.append("Visual evidence (Take a photo or upload an image)")
        if not category or category == "Select category":
            missing.append("Issue Category")
        if not st.session_state.get("location_text") or not st.session_state.get("location_text").strip():
            missing.append("Location Address (Detect via GPS or enter manually)")
        if not description or not description.strip():
            missing.append("Description")

        if missing:
            st.error(f"⚠️ Incomplete submission. Please provide: {', '.join(missing)}")
        else:
            try:
                img_obj = Image.open(final_image)
                ai_data = st.session_state.get("ai_result") if (st.session_state.get("ai_result") and st.session_state.get("ai_result").get("success")) else None

                record = create_complaint_record(
                    category=category,
                    description=description,
                    location_text=st.session_state.get("location_text"),
                    latitude=st.session_state.get("gps_latitude"),
                    longitude=st.session_state.get("gps_longitude"),
                    image_file=img_obj,
                    ai_category=ai_data.get("category") if ai_data else None,
                    ai_confidence=ai_data.get("confidence") if ai_data else None,
                    ai_confidence_level=ai_data.get("confidence_level") if ai_data else None,
                    ai_reason=ai_data.get("reason") if ai_data else None,
                    ai_summary=ai_data.get("summary") if ai_data else None,
                    severity=ai_data.get("severity") if ai_data else "Medium",
                    priority_score=ai_data.get("priority_score") if ai_data else 50,
                    risk_factors=ai_data.get("risk_factors") if ai_data else [],
                    recommended_action=ai_data.get("recommended_action") if ai_data else "",
                    is_duplicate_of=matched_duplicate_cid
                )

                # Persist to local JSON storage
                saved_record = save_complaint(record)
                if matched_duplicate_cid:
                    link_duplicate_complaint(saved_record["complaint_id"], matched_duplicate_cid)

                st.session_state["complaints"] = load_all_complaints()
                st.session_state["submitted_complaint"] = saved_record
                st.rerun()
            except Exception as e:
                st.error(f"Error processing report: {str(e)}")


def render_stepper_html(current_status: str) -> str:
    """
    Renders an HTML lifecycle progress stepper showing complaint transition states.
    """
    steps = [
        ("SUBMITTED", "Submitted"),
        ("UNDER_REVIEW", "Under Review"),
        ("ASSIGNED", "Assigned"),
        ("IN_PROGRESS", "In Progress"),
        ("RESOLVED", "Resolved")
    ]

    status_order = {s[0]: i for i, s in enumerate(steps)}
    current_idx = status_order.get(current_status, 0)
    if current_status == "REJECTED":
        return """<div class="stepper-container" style="border-left: 3px solid #EF4444;">
<span class="status-badge status-rejected" style="font-size: 0.8rem; padding: 4px 10px;">REJECTED / CLOSED</span>
<span style="font-size: 0.82rem; color: #888; margin-left: 12px;">This complaint has been reviewed and marked as non-actionable or duplicate.</span>
</div>"""

    steps_html = []
    for i, (code, label) in enumerate(steps):
        if i < current_idx:
            cls = "completed"
            dot_content = "✓"
        elif i == current_idx:
            cls = "active"
            dot_content = str(i + 1)
        else:
            cls = ""
            dot_content = str(i + 1)

        steps_html.append(f"""<div class="stepper-step {cls}">
<div class="stepper-dot">{dot_content}</div>
<div class="stepper-label">{label}</div>
</div>""")

    return f"""<div class="stepper-container">
{"".join(steps_html)}
</div>"""


def render_track():
    """
    Renders the enhanced Track page with search, filters, SLA status badges,
    and side-by-side Before/After resolution proof cards.
    """
    st.markdown(
        """<div class="eyebrow">CITIZEN VERIFICATION & TRACKING</div>
<div class="headline-hero" style="font-size: 2.8rem; margin-bottom: 0.5rem;">
Track your reports.
</div>
<div class="headline-sub" style="font-size: 1.15rem; color: #888888; margin-bottom: 2rem;">
Monitor real-time municipal triage, SLA countdowns, and verified resolution evidence.
</div>""",
        unsafe_allow_html=True
    )

    complaints_list = load_all_complaints()
    st.session_state["complaints"] = complaints_list

    if not complaints_list:
        st.markdown(
            """<div style="border: 1px solid #1A1A1A; padding: 3.5rem 2rem; text-align: center; margin-bottom: 2rem; background: #080808;">
<div style="font-size: 1.2rem; font-weight: 700; color: #EBEBEB; margin-bottom: 0.4rem;">Nothing here yet.</div>
<div style="font-size: 0.9rem; color: #888888; margin-bottom: 1.5rem;">Your submitted civic reports will appear here.</div>
</div>""",
            unsafe_allow_html=True
        )
        if st.button("Report an Issue →", key="track_empty_cta", type="primary"):
            set_page("Report an Issue")
        return

    # Search & Filter Controls
    f_col1, f_col2, f_col3 = st.columns([2.5, 1.2, 1.3], gap="medium")
    with f_col1:
        search_kw = st.text_input(
            "Search reports",
            placeholder="Search by Complaint ID (e.g. SC-2026-...), address, or keyword",
            label_visibility="collapsed",
            key="track_search_input"
        )
    with f_col2:
        status_filter = st.selectbox(
            "Filter by status",
            options=["All Statuses"] + COMPLAINT_STATUSES,
            label_visibility="collapsed",
            key="track_status_filter_select"
        )
    with f_col3:
        cat_filter = st.selectbox(
            "Filter by category",
            options=["All Categories"] + CIVIC_CATEGORIES,
            label_visibility="collapsed",
            key="track_cat_filter_select"
        )

    # Filter evaluation
    filtered = []
    for c in complaints_list:
        if status_filter != "All Statuses" and c.get("status") != status_filter:
            continue
        if cat_filter != "All Categories" and c.get("category") != cat_filter:
            continue
        if search_kw and search_kw.strip():
            kw = search_kw.strip().lower()
            match = (
                kw in str(c.get("complaint_id", "")).lower() or
                kw in str(c.get("location_text", "")).lower() or
                kw in str(c.get("description", "")).lower() or
                kw in str(c.get("category", "")).lower() or
                kw in str(c.get("assigned_department", "")).lower()
            )
            if not match:
                continue
        filtered.append(c)

    st.markdown(
        f"""<div style="display: flex; justify-content: space-between; align-items: center; margin: 1rem 0; font-size: 0.82rem; color: #888;">
<div>Displaying <strong>{len(filtered)}</strong> of {len(complaints_list)} reports</div>
<div>Storage: <code>%LOCALAPPDATA%/SmartCivic/data</code> (Persistent)</div>
</div>""",
        unsafe_allow_html=True
    )

    if not filtered:
        st.info("No complaints match the selected search or filter criteria.")
        return

    # Render Table & Expandable Detail Cards
    st.markdown(
        """<div class="track-row header">
<div>COMPLAINT ID</div>
<div>CATEGORY</div>
<div>LOCATION / COORDINATES</div>
<div>AI TRIAGE & SEVERITY</div>
<div>STATUS & SLA</div>
<div>TIMESTAMP</div>
</div>""",
        unsafe_allow_html=True
    )

    for c in reversed(filtered):
        cid = c.get("complaint_id", "N/A")
        cat = c.get("category", "Uncategorized")
        loc = c.get("location_text", "N/A")
        lat = c.get("latitude")
        lon = c.get("longitude")
        status = c.get("status") or "SUBMITTED"
        timestamp = c.get("timestamp") or "N/A"
        sev = c.get("severity") or "Medium"
        prio = c.get("priority_score") if c.get("priority_score") is not None else 50
        dept = c.get("assigned_department") or "Unassigned"

        conf_val = c.get("ai_confidence")
        if conf_val is not None:
            try:
                conf_str = f"{int(float(conf_val) * 100)}%"
            except (ValueError, TypeError):
                conf_str = "N/A"
        else:
            conf_str = "N/A"

        status_slug = str(status).lower().replace(" ", "_")
        sev_lower = str(sev).lower()
        sev_cls = f"severity-{sev_lower}" if sev_lower in ["low", "medium", "high", "critical"] else "severity-medium"

        sla_info = calculate_sla_status(c)
        sla_cls = "sla-breached" if sla_info["is_breached"] else ("sla-expiring" if sla_info["is_nearing_breach"] else "sla-ontrack")

        coords_sub = ""
        if lat is not None and lon is not None:
            coords_sub = f"<div style='font-family: monospace; font-size: 0.75rem; color: #B15258; margin-top: 2px;'>{lat:.6f}, {lon:.6f}</div>"

        ai_cell = "<span style='color: #555; font-size: 0.75rem;'>Manual</span>"
        if c.get("is_ai_analyzed"):
            ai_cell = f"""<div style="display: flex; flex-direction: column; gap: 3px;">
<span class='diagram-badge active-ai' style='font-size: 0.65rem;'>🤖 AI ({conf_str})</span>
<span class='ai-severity-badge {sev_cls}' style='font-size: 0.62rem; padding: 1px 5px;'>{sev.upper()} · {prio}/100</span>
</div>"""

        row_html = f"""<div class="track-row">
<div style="font-family: monospace; color: #C45D63; font-weight: 700;">{cid}</div>
<div style="color: #EBEBEB;">{cat}</div>
<div style="color: #888888; font-size: 0.85rem;">{loc}{coords_sub}</div>
<div>{ai_cell}</div>
<div>
<span class="status-badge status-{status_slug}">{status.replace('_', ' ')}</span>
<div style="margin-top: 3px;"><span class="sla-badge {sla_cls}">{sla_info['sla_badge']}</span></div>
</div>
<div style="color: #666666; font-size: 0.82rem;">{timestamp}</div>
</div>"""
        st.markdown(row_html, unsafe_allow_html=True)

        # Expandable Detailed Ticket View
        with st.expander(f"📋 View Full Lifecycle Ticket & Evidence: {cid}"):
            # 1. Lifecycle Stepper
            st.markdown(render_stepper_html(status), unsafe_allow_html=True)

            # 2. Detailed Split View
            d_col1, d_col2 = st.columns([1.1, 0.9], gap="large")
            with d_col1:
                st.markdown("<div class='ai-field-label'>CITIZEN DESCRIPTION</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='color: #E5E5E5; margin-bottom: 1rem; font-size: 0.92rem; line-height: 1.5;'>{c.get('description', 'No description provided.')}</div>", unsafe_allow_html=True)

                st.markdown("<div class='ai-field-label'>LOCATION & MAPPING</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='color: #CCCCCC; font-size: 0.88rem; margin-bottom: 0.4rem;'>{loc}</div>", unsafe_allow_html=True)
                if lat is not None and lon is not None:
                    maps_link = f"https://www.google.com/maps?q={lat},{lon}"
                    st.markdown(
                        f"""<div style='margin-bottom: 1rem;'>
<span style='font-family: monospace; font-size: 0.8rem; color: #B15258;'>{lat:.6f}, {lon:.6f}</span>
<a href='{maps_link}' target='_blank' style='margin-left: 10px; color: #60A5FA; font-size: 0.78rem; text-decoration: none;'>View on Google Maps ↗</a>
</div>""",
                        unsafe_allow_html=True
                    )

                # -------------------------------------------------------------
                # v0.5 RESOLUTION VERIFICATION ("BEFORE & AFTER" PROOF CARD)
                # -------------------------------------------------------------
                img_path = c.get("image_path")
                res_img_path = c.get("resolution_image_path")

                if res_img_path:
                    st.markdown("<div class='ai-field-label' style='color: #34D399;'>✓ RESOLUTION VERIFICATION EVIDENCE (BEFORE VS. AFTER)</div>", unsafe_allow_html=True)
                    p_col1, p_col2 = st.columns(2, gap="small")
                    with p_col1:
                        st.markdown("<div class='proof-badge proof-before' style='margin-bottom: 4px;'>BEFORE REPAIR (CITIZEN)</div>", unsafe_allow_html=True)
                        if img_path:
                            r_before = (PROJECT_ROOT / img_path) if not os.path.isabs(str(img_path)) else Path(img_path)
                            if r_before.exists():
                                st.image(str(r_before), use_container_width=True)
                    with p_col2:
                        st.markdown("<div class='proof-badge proof-after' style='margin-bottom: 4px;'>AFTER REPAIR (MUNICIPAL PROOF)</div>", unsafe_allow_html=True)
                        r_after = (PROJECT_ROOT / res_img_path) if not os.path.isabs(str(res_img_path)) else Path(res_img_path)
                        if r_after.exists():
                            st.image(str(r_after), use_container_width=True)
                else:
                    st.markdown("<div class='ai-field-label'>ATTACHED PHOTO EVIDENCE</div>", unsafe_allow_html=True)
                    img_rendered = False
                    if img_path:
                        resolved_img_path = (PROJECT_ROOT / img_path) if not os.path.isabs(str(img_path)) else Path(img_path)
                        if resolved_img_path.exists():
                            try:
                                st.image(str(resolved_img_path), caption=f"Evidence for {cid}", use_container_width=True)
                                img_rendered = True
                            except Exception:
                                pass
                    if not img_rendered:
                        st.markdown("<div style='color: #666; font-size: 0.8rem; font-style: italic;'>Synthetic/demo evidence record.</div>", unsafe_allow_html=True)

            with d_col2:
                # AI Triage Breakdown
                st.markdown(
                    f"""<div style="background: #060606; border: 1px solid #1A1A1A; padding: 1.2rem; margin-bottom: 1rem;">
<div style="font-size: 0.7rem; font-weight: 800; color: #A3A3A3; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.6rem;">AI TRIAGE & SLA GOVERNANCE</div>
<div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.8rem;">
<span style="font-size: 1.1rem; font-weight: 700; color: #FFF;">{cat}</span>
<span class="ai-confidence-badge">{conf_str} Conf</span>
</div>
<div style="margin-bottom: 0.8rem;">
<span class="ai-severity-badge {sev_cls}">{sev} SEVERITY</span>
<span style="font-family: monospace; color: #E5E5E5; margin-left: 8px; font-weight: 700;">{prio}/100 Priority</span>
</div>
<div style="margin-bottom: 0.8rem;">
<span class="sla-badge {sla_cls}">{sla_info['sla_badge']}</span>
<span style="font-size: 0.78rem; color: #888; margin-left: 8px;">Target: {sla_info['target_hours']}h (Deadline: {sla_info['deadline_str']})</span>
</div>
<div class="ai-field-label">AI SUMMARY</div>
<div style="font-size: 0.85rem; color: #CCC; margin-bottom: 0.8rem; line-height: 1.4;">{c.get('ai_summary', 'N/A')}</div>
<div class="ai-field-label">RECOMMENDED ACTION</div>
<div style="font-size: 0.85rem; color: #10B981; line-height: 1.4;">{c.get('recommended_action', 'N/A')}</div>
</div>""",
                    unsafe_allow_html=True
                )

                st.markdown("<div class='ai-field-label'>ASSIGNED MUNICIPAL DEPARTMENT</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='color: #FBBF24; font-size: 0.88rem; font-weight: 600; margin-bottom: 1rem;'>{dept}</div>", unsafe_allow_html=True)

                if c.get("resolution_notes"):
                    st.markdown("<div class='ai-field-label'>RESOLUTION / DISPATCH NOTES</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='color: #34D399; font-size: 0.85rem; background: rgba(52, 211, 153, 0.08); border-left: 2px solid #34D399; padding: 6px 10px; margin-bottom: 1rem;'>{c.get('resolution_notes')}</div>", unsafe_allow_html=True)

            # 3. Status History Timeline
            history = c.get("status_history", [])
            if history:
                st.markdown("<div class='ai-field-label' style='margin-top: 1rem;'>STATUS AUDIT TRAIL</div>", unsafe_allow_html=True)
                for h in history:
                    st.markdown(
                        f"""<div style="display: flex; gap: 15px; font-size: 0.8rem; padding: 4px 0; border-bottom: 1px solid #111;">
<span style="font-family: monospace; color: #888;">{h.get('timestamp')}</span>
<span class="status-badge status-{h.get('status', 'SUBMITTED').lower()}">{h.get('status')}</span>
<span style="color: #CCC;">{h.get('note')}</span>
</div>""",
                        unsafe_allow_html=True
                    )


def render_gis_map():
    """
    Renders the interactive Geospatial Incident Map & Hotspot Visualizer.
    """
    st.markdown(
        """<div class="eyebrow">GEOSPATIAL INTELLIGENCE & GIS MAPPING</div>
<div class="headline-hero" style="font-size: 2.8rem; margin-bottom: 0.5rem;">
Interactive City Incident Map.
</div>
<div class="headline-sub" style="font-size: 1.15rem; color: #888888; margin-bottom: 1.8rem;">
Real-time geospatial clustering, severity distribution, and ward hotspot density layers.
</div>""",
        unsafe_allow_html=True
    )

    complaints_list = load_all_complaints()

    # Map Toolbar & Filters
    m_col1, m_col2, m_col3, m_col4 = st.columns([1.5, 1.2, 1.2, 1.1], gap="medium")
    with m_col1:
        map_cat_filter = st.selectbox(
            "Filter Category",
            options=["All Categories"] + CIVIC_CATEGORIES,
            key="map_cat_filter_sel"
        )
    with m_col2:
        map_sev_filter = st.selectbox(
            "Filter Severity",
            options=["All Severities", "Critical", "High", "Medium", "Low"],
            key="map_sev_filter_sel"
        )
    with m_col3:
        map_status_filter = st.selectbox(
            "Filter Status",
            options=["All Statuses"] + COMPLAINT_STATUSES,
            key="map_status_filter_sel"
        )
    with m_col4:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        show_heatmap = st.checkbox("🔥 Heatmap Layer", value=False, key="map_heat_toggle")

    # Filter evaluation for map
    map_filtered = []
    for c in complaints_list:
        if map_cat_filter != "All Categories" and c.get("category") != map_cat_filter:
            continue
        if map_sev_filter != "All Severities" and c.get("severity") != map_sev_filter:
            continue
        if map_status_filter != "All Statuses" and c.get("status") != map_status_filter:
            continue
        map_filtered.append(c)

    # Render PyDeck Interactive Map
    render_gis_map_component(map_filtered, show_heatmap=show_heatmap)

    # Ward Summary Legend
    st.markdown(
        """<div style="display: flex; gap: 20px; align-items: center; justify-content: center; font-size: 0.8rem; margin: 1rem 0 2rem 0; color: #888;">
<div><span style="color: #EF4444; font-size: 1.1rem;">●</span> Critical Severity (Prio ≥ 75)</div>
<div><span style="color: #F97316; font-size: 1.1rem;">●</span> High Severity (Prio 50-74)</div>
<div><span style="color: #F59E0B; font-size: 1.1rem;">●</span> Medium Severity (Prio 25-49)</div>
<div><span style="color: #10B981; font-size: 1.1rem;">●</span> Low Severity (Prio 0-24)</div>
</div>""",
        unsafe_allow_html=True
    )


def render_analytics_and_triage():
    """
    Renders the Municipal Governance & Operations Dashboard with real-time KPI cards,
    visual category/severity/status distributions, CSV export, and priority-sorted triage queue.
    """
    st.markdown(
        """<div class="eyebrow">MUNICIPAL GOVERNANCE & OPERATIONS</div>
<div class="headline-hero" style="font-size: 2.8rem; margin-bottom: 0.5rem;">
Civic Analytics & Triage.
</div>
<div class="headline-sub" style="font-size: 1.15rem; color: #888888; margin-bottom: 2rem;">
Real-time incident triage queue, SLA turnaround metrics, resolution proof verification, and work-order export.
</div>""",
        unsafe_allow_html=True
    )

    complaints_list = load_all_complaints()
    st.session_state["complaints"] = complaints_list
    analytics = compute_municipal_analytics(complaints_list)

    # -------------------------------------------------------------
    # SECTION 1: Real-Time Municipal KPI Summary Cards (v0.5)
    # -------------------------------------------------------------
    st.markdown(
        f"""<div class="kpi-grid">
<div class="kpi-card accent-blue">
<div class="kpi-label">TOTAL LOGGED</div>
<div class="kpi-number">{analytics['total_complaints']}</div>
<div class="kpi-subtext">Cumulative citizen reports</div>
</div>
<div class="kpi-card accent-amber">
<div class="kpi-label">PENDING TRIAGE</div>
<div class="kpi-number">{analytics['pending_count']}</div>
<div class="kpi-subtext">Submitted & Under Review</div>
</div>
<div class="kpi-card accent-purple">
<div class="kpi-label">IN PROGRESS</div>
<div class="kpi-number">{analytics['in_progress_count']}</div>
<div class="kpi-subtext">Assigned & Field Ops</div>
</div>
<div class="kpi-card accent-green">
<div class="kpi-label">SLA COMPLIANCE</div>
<div class="kpi-number">{analytics['sla_compliance_pct']}%</div>
<div class="kpi-subtext">{analytics['sla_on_track_count']} of {analytics['total_complaints']} On-Track</div>
</div>
<div class="kpi-card accent-red">
<div class="kpi-label">SLA BREACHED</div>
<div class="kpi-number">{analytics['sla_breached_count']}</div>
<div class="kpi-subtext">Overdue Turnaround</div>
</div>
<div class="kpi-card">
<div class="kpi-label">AVG PRIORITY</div>
<div class="kpi-number">{analytics['avg_priority_score']}</div>
<div class="kpi-subtext">System-wide urgency / 100</div>
</div>
</div>""",
        unsafe_allow_html=True
    )

    # -------------------------------------------------------------
    # SECTION 2: Data Intelligence & Export Toolbar
    # -------------------------------------------------------------
    st.markdown("<hr class='editorial-divider'>", unsafe_allow_html=True)
    st.markdown("<div class='eyebrow'>DATA INTELLIGENCE & EXPORT</div>", unsafe_allow_html=True)
    
    exp_col1, exp_col2 = st.columns([2.5, 1.5], gap="medium")
    with exp_col1:
        st.markdown("<div class='section-headline' style='margin-bottom: 0.5rem;'>Incident Distribution & Workload Analysis</div>", unsafe_allow_html=True)
    with exp_col2:
        csv_data = generate_complaints_csv(complaints_list)
        st.download_button(
            "📥 Export Full Incident Log (CSV)",
            data=csv_data,
            file_name=f"smartcivic_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True,
            key="btn_export_csv"
        )

    dist_col1, dist_col2 = st.columns(2, gap="large")

    with dist_col1:
        # Category Distribution Card
        cat_dist = analytics["category_distribution"]
        total_c = max(1, analytics["total_complaints"])
        
        cat_bars_html = []
        for cat_name in CIVIC_CATEGORIES:
            cnt = cat_dist.get(cat_name, 0)
            pct = int((cnt / total_c) * 100)
            cat_bars_html.append(f"""<div class="analytics-bar-item">
<div class="analytics-bar-header">
<span>{cat_name}</span>
<span><strong>{cnt}</strong> ({pct}%)</span>
</div>
<div class="analytics-bar-track">
<div class="analytics-bar-fill" style="width: {pct}%;"></div>
</div>
</div>""")

        st.markdown(
            f"""<div class="analytics-dist-card">
<div class="analytics-dist-title">REPORTS BY CIVIC CATEGORY</div>
{"".join(cat_bars_html)}
</div>""",
            unsafe_allow_html=True
        )

        # Severity Level Distribution Card
        sev_dist = analytics["severity_distribution"]
        sev_colors = {"Critical": "#EF4444", "High": "#F97316", "Medium": "#F59E0B", "Low": "#10B981"}
        sev_bars_html = []
        for s_level in ["Critical", "High", "Medium", "Low"]:
            s_cnt = sev_dist.get(s_level, 0)
            s_pct = int((s_cnt / total_c) * 100)
            s_col = sev_colors.get(s_level, "#F59E0B")
            sev_bars_html.append(f"""<div class="analytics-bar-item">
<div class="analytics-bar-header">
<span>{s_level} Severity</span>
<span style="color: {s_col};"><strong>{s_cnt}</strong> ({s_pct}%)</span>
</div>
<div class="analytics-bar-track">
<div class="analytics-bar-fill" style="width: {s_pct}%; background: {s_col};"></div>
</div>
</div>""")

        st.markdown(
            f"""<div class="analytics-dist-card">
<div class="analytics-dist-title">REPORTS BY SEVERITY TIER</div>
{"".join(sev_bars_html)}
</div>""",
            unsafe_allow_html=True
        )

    with dist_col2:
        # Status Workflow Breakdown
        st_dist = analytics["status_distribution"]
        st_bars_html = []
        for st_name in COMPLAINT_STATUSES:
            st_cnt = st_dist.get(st_name, 0)
            st_pct = int((st_cnt / total_c) * 100)
            st_bars_html.append(f"""<div class="analytics-bar-item">
<div class="analytics-bar-header">
<span>{st_name.replace('_', ' ')}</span>
<span><strong>{st_cnt}</strong> ({st_pct}%)</span>
</div>
<div class="analytics-bar-track">
<div class="analytics-bar-fill" style="width: {st_pct}%; background: #60A5FA;"></div>
</div>
</div>""")

        st.markdown(
            f"""<div class="analytics-dist-card">
<div class="analytics-dist-title">LIFECYCLE STATUS WORKFLOW</div>
{"".join(st_bars_html)}
</div>""",
            unsafe_allow_html=True
        )

        # Municipal Department Workload
        dept_dist = analytics["department_workload"]
        dept_bars_html = []
        for d_name in MUNICIPAL_DEPARTMENTS:
            d_cnt = dept_dist.get(d_name, 0)
            d_pct = int((d_cnt / total_c) * 100)
            dept_bars_html.append(f"""<div class="analytics-bar-item">
<div class="analytics-bar-header">
<span style="font-size: 0.78rem;">{d_name}</span>
<span><strong>{d_cnt}</strong> ({d_pct}%)</span>
</div>
<div class="analytics-bar-track">
<div class="analytics-bar-fill" style="width: {d_pct}%; background: #FBBF24;"></div>
</div>
</div>""")

        st.markdown(
            f"""<div class="analytics-dist-card">
<div class="analytics-dist-title">WORKLOAD BY MUNICIPAL DEPARTMENT</div>
{"".join(dept_bars_html)}
</div>""",
            unsafe_allow_html=True
        )

    # -------------------------------------------------------------
    # SECTION 3: Priority-Sorted Municipal Triage Queue & Resolution
    # -------------------------------------------------------------
    st.markdown("<hr class='editorial-divider'>", unsafe_allow_html=True)
    st.markdown("<div class='eyebrow'>FIELD OPERATIONS & DISPATCH</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-headline' style='margin-bottom: 0.5rem;'>Priority-Ranked Municipal Triage Queue</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 0.9rem; color: #888; margin-bottom: 1.5rem;'>Critical and high-priority incidents automatically float to the top for rapid field allocation and resolution verification.</div>", unsafe_allow_html=True)

    # Triage Queue Filter Controls
    t_col1, t_col2, t_col3 = st.columns([1, 1, 1.2], gap="medium")
    with t_col1:
        t_status_filter = st.selectbox(
            "Triage Status Filter",
            options=["All Statuses"] + COMPLAINT_STATUSES,
            key="triage_status_filter_sel"
        )
    with t_col2:
        t_sev_filter = st.selectbox(
            "Triage Severity Filter",
            options=["All Severities", "Critical", "High", "Medium", "Low"],
            key="triage_sev_filter_sel"
        )
    with t_col3:
        t_dept_filter = st.selectbox(
            "Triage Department Filter",
            options=["All Departments"] + MUNICIPAL_DEPARTMENTS,
            key="triage_dept_filter_sel"
        )

    # Printable Dispatch Brief Expander
    with st.expander("📋 View Printable Municipal Field Dispatch Sheet"):
        dispatch_md = generate_work_order_dispatch_sheet(complaints_list, t_dept_filter)
        st.markdown(dispatch_md)

    # Priority-Sort: highest priority score first, then newest timestamp
    sorted_queue = sorted(
        complaints_list,
        key=lambda x: (x.get("priority_score", 0), str(x.get("timestamp", ""))),
        reverse=True
    )

    triage_filtered = []
    for c in sorted_queue:
        if t_status_filter != "All Statuses" and c.get("status") != t_status_filter:
            continue
        if t_sev_filter != "All Severities" and c.get("severity") != t_sev_filter:
            continue
        if t_dept_filter != "All Departments" and c.get("assigned_department") != t_dept_filter:
            continue
        triage_filtered.append(c)

    st.caption(f"Showing {len(triage_filtered)} tickets matching triage criteria.")

    if not triage_filtered:
        st.success("✓ No pending issues match the current triage filter.")
        return

    # Render Triage Cards with Action Panels & Resolution Photo Upload
    for item in triage_filtered:
        cid = item.get("complaint_id") or "N/A"
        cat = item.get("category") or "Uncategorized"
        loc = item.get("location_text") or "N/A"
        status = item.get("status") or "SUBMITTED"
        sev = item.get("severity") or "Medium"
        prio = item.get("priority_score") if item.get("priority_score") is not None else 50
        dept = item.get("assigned_department") or "Unassigned"
        time_str = item.get("timestamp") or "N/A"
        action = item.get("recommended_action") or "Inspect and take action."
        desc = item.get("description") or "No description."
        sev_lower = str(sev).lower()
        sev_cls = f"severity-{sev_lower}" if sev_lower in ["low", "medium", "high", "critical"] else "severity-medium"
        prio_border = f"prio-{sev_lower}" if sev_lower in ["low", "medium", "high", "critical"] else "prio-medium"

        sla_info = calculate_sla_status(item)
        sla_cls = "sla-breached" if sla_info["is_breached"] else ("sla-expiring" if sla_info["is_nearing_breach"] else "sla-ontrack")

        duplicate_sub = ""
        if item.get("duplicate_count", 0) > 0:
            duplicate_sub = f"<span style='color: #F59E0B; font-size: 0.8rem; font-weight: 700; margin-left: 10px;'>+{item.get('duplicate_count')} Citizen Verifications</span>"

        st.markdown(
            f"""<div class="triage-ticket-card {prio_border}">
<div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.6rem;">
<div>
<span style="font-family: monospace; font-size: 1.15rem; font-weight: 800; color: #FFF;">{cid}</span>
<span style="color: #888; font-size: 0.85rem; margin-left: 10px;">{time_str}</span>
{duplicate_sub}
</div>
<div>
<span class="sla-badge {sla_cls}">{sla_info['sla_badge']}</span>
<span class="ai-severity-badge {sev_cls}" style="margin-left: 6px;">{sev}</span>
<span style="font-family: monospace; font-size: 1.1rem; font-weight: 800; color: #E5E5E5; margin-left: 8px;">{prio}/100 PRIORITY</span>
</div>
</div>
<div style="font-size: 1.2rem; font-weight: 700; color: #E5E5E5; margin-bottom: 0.4rem;">{cat}</div>
<div style="font-size: 0.85rem; color: #888; margin-bottom: 0.8rem;">📍 {loc}</div>
<div style="font-size: 0.9rem; color: #CCC; margin-bottom: 0.8rem; line-height: 1.4;">{desc}</div>
<div style="font-size: 0.82rem; color: #10B981; margin-bottom: 0.8rem;">💡 Recommended Action: {action}</div>
</div>""",
            unsafe_allow_html=True
        )

        # Interactive Status, Department Assignment, and Proof Upload Box
        with st.container():
            u_col1, u_col2, u_col3, u_col4 = st.columns([1.4, 2.3, 3.2, 1.1], gap="small")
            
            with u_col1:
                cur_status_idx = COMPLAINT_STATUSES.index(status) if status in COMPLAINT_STATUSES else 0
                new_st = st.selectbox(
                    "Update Status",
                    options=COMPLAINT_STATUSES,
                    index=cur_status_idx,
                    key=f"status_sel_{cid}"
                )

            with u_col2:
                cur_dept_idx = MUNICIPAL_DEPARTMENTS.index(dept) if dept in MUNICIPAL_DEPARTMENTS else 0
                new_dept = st.selectbox(
                    "Assign Department",
                    options=MUNICIPAL_DEPARTMENTS,
                    index=cur_dept_idx,
                    key=f"dept_sel_{cid}"
                )

            with u_col3:
                res_note = st.text_input(
                    "Resolution / Dispatch Notes",
                    value=item.get("resolution_notes", ""),
                    placeholder="Enter dispatch notes or repair details...",
                    key=f"note_input_{cid}"
                )

            with u_col4:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                save_btn = st.button("Save", key=f"btn_save_{cid}", type="primary", use_container_width=True)

            # Resolution Proof Upload (Only shown when marking RESOLVED)
            res_proof_img = None
            if new_st == "RESOLVED":
                st.markdown("<div style='font-size: 0.78rem; font-weight: 700; color: #34D399; margin-top: 4px;'>📷 ATTACH FIELD RESOLUTION PROOF PHOTO (AFTER REPAIR):</div>", unsafe_allow_html=True)
                res_proof_img = st.file_uploader(
                    "Upload After Repair Proof Photo",
                    type=["jpg", "jpeg", "png"],
                    key=f"res_proof_upload_{cid}",
                    label_visibility="collapsed"
                )

            if save_btn:
                pil_proof = Image.open(res_proof_img) if res_proof_img is not None else None
                ok = update_complaint_status(
                    complaint_id=cid,
                    new_status=new_st,
                    note=res_note,
                    assigned_department=new_dept,
                    resolution_image=pil_proof
                )
                if ok:
                    st.toast(f"✓ Ticket {cid} updated to {new_st}!", icon="📋")
                    st.session_state["complaints"] = load_all_complaints()
                    st.rerun()
                else:
                    st.error("Failed to update complaint record.")

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)


def render_about():
    """
    Renders the About page with the evolution roadmap.
    """
    st.markdown(
        """<div class="eyebrow">PLATFORM VISION</div>
<div class="headline-hero" style="font-size: 2.8rem; margin-bottom: 0.5rem;">
Technology for better cities.
</div>
<div class="headline-sub" style="font-size: 1.15rem; color: #888888; margin-bottom: 2.5rem;">
Bridging citizen vigilance with intelligent municipal dispatch, geospatial intelligence, and transparent governance.
</div>""",
        unsafe_allow_html=True
    )

    col_about_text, col_about_meta = st.columns([2, 1], gap="large")

    with col_about_text:
        st.markdown(
            """<div style="font-size: 1.15rem; color: #C8C8C8; line-height: 1.7; margin-bottom: 2rem;">
SmartCivic is an intelligent civic reporting platform engineered to streamline 
urban issue resolution. By standardizing report intake and establishing an AI-ready data foundation, 
SmartCivic connects public reports with municipal authorities through priority triage, persistent lifecycle tracking, 
geospatial clustering, and data analytics.
</div>""",
            unsafe_allow_html=True
        )

    with col_about_meta:
        st.markdown(
            """<div style="border: 1px solid #1A1A1A; padding: 1.5rem; background: #080808;">
<div style="font-size: 0.72rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #B15258; margin-bottom: 0.5rem;">
PROJECT SPECIFICATIONS
</div>
<div style="font-size: 0.88rem; color: #888888; line-height: 1.6;">
Release: <strong>v0.5 GIS & SLA Engine</strong><br>
AI Vision: <strong>Google Gemini Flash Multimodal</strong><br>
Triage: <strong>Severity + Priority + Risk Assessment</strong><br>
Geospatial: <strong>PyDeck Scatter & Heatmap GIS</strong><br>
Operations: <strong>SLA Timers + Resolution Proof</strong><br>
Context: <strong>Smart India Hackathon</strong>
</div>
</div>""",
            unsafe_allow_html=True
        )

    st.markdown("<hr class='editorial-divider'>", unsafe_allow_html=True)

    st.markdown(
        """<div class="eyebrow">ROADMAP</div>
<div class="section-headline">How SmartCivic evolves.</div>""",
        unsafe_allow_html=True
    )

    timeline = [
        ("01", "FOUNDATION", "Camera capture, browser GPS detection, reverse geocoding auto-fill, dynamic ID generation, and structured session store. (Completed in v0.1)"),
        ("02", "INTELLIGENCE", "Gemini multimodal vision AI issue classification, confidence scoring, visual evidence summary, and citizen review. (Completed in v0.2)"),
        ("03", "RISK & SEVERITY", "Unified multimodal severity triage (Low/Medium/High/Critical), 0-100 priority scoring, risk factors, and recommended action. (Completed in v0.3)"),
        ("04", "MANAGEMENT & ANALYTICS", "Persistent complaint storage, lifecycle status workflow (Submitted→Resolved), search & filters, and municipal analytics dashboard. (Completed in v0.4)"),
        ("05", "GEOSPATIAL & SLA GOVERNANCE", "Interactive GIS map with heatmap layers, automated duplicate proximity clustering, Before/After resolution verification, and SLA countdown engine. (Active in v0.5)")
    ]

    for num, title, desc in timeline:
        timeline_html = f"""<div class="timeline-editorial-item">
<div class="timeline-editorial-ver">{num} — {title}</div>
<div class="timeline-editorial-title">{title}</div>
<div class="timeline-editorial-desc">{desc}</div>
</div>"""
        st.markdown(timeline_html, unsafe_allow_html=True)


def main():
    """
    Main application router with v0.5 GIS Map support.
    """
    render_top_navigation()

    page = st.session_state.get("page", "Home")

    if page == "Home":
        render_home()
    elif page == "Report an Issue":
        render_report()
    elif page == "Track":
        render_track()
    elif page == "GIS Map":
        render_gis_map()
    elif page == "Analytics & Triage":
        render_analytics_and_triage()
    elif page == "About":
        render_about()


if __name__ == "__main__":
    main()
