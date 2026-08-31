from typing import Any, Dict, List, Optional
import pandas as pd
import pydeck as pdk
import streamlit as st

SEVERITY_COLORS = {
    "Critical": [239, 68, 68, 230],   # Red
    "High": [249, 115, 22, 230],       # Orange
    "Medium": [245, 158, 11, 230],     # Amber
    "Low": [16, 185, 129, 230]         # Green
}


def build_geospatial_dataframe(complaints: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Transforms complaint records into a validated pandas DataFrame formatted
    for PyDeck geospatial rendering with color coordinates and formatted tooltips.
    """
    rows = []
    for c in complaints:
        lat = c.get("latitude")
        lon = c.get("longitude")
        if lat is None or lon is None:
            continue

        sev = c.get("severity") or "Medium"
        color = SEVERITY_COLORS.get(sev, [245, 158, 11, 230])
        prio = c.get("priority_score") if c.get("priority_score") is not None else 50
        # Dynamic pin radius scaled by priority score
        radius = 18 + int(prio * 0.35)

        rows.append({
            "complaint_id": c.get("complaint_id", "N/A"),
            "category": c.get("category", "General"),
            "severity": sev,
            "priority_score": prio,
            "status": c.get("status", "SUBMITTED"),
            "location_text": c.get("location_text", "Location unavailable"),
            "timestamp": c.get("timestamp", ""),
            "department": c.get("assigned_department", "Unassigned"),
            "lat": float(lat),
            "lon": float(lon),
            "color_r": color[0],
            "color_g": color[1],
            "color_b": color[2],
            "color_a": color[3],
            "radius": radius
        })

    if not rows:
        return pd.DataFrame(columns=["lat", "lon", "complaint_id", "category", "severity", "priority_score", "status", "location_text", "color_r", "color_g", "color_b", "color_a", "radius"])

    return pd.DataFrame(rows)


def render_gis_map_component(
    complaints: List[Dict[str, Any]],
    show_heatmap: bool = False,
    selected_cid: Optional[str] = None
) -> None:
    """
    Renders an interactive PyDeck GIS scatter and density map component inside Streamlit.
    """
    df = build_geospatial_dataframe(complaints)

    if df.empty:
        st.markdown(
            """<div style="border: 1px solid #1A1A1A; padding: 2.5rem; text-align: center; background: #080808; margin-bottom: 1.5rem;">
<div style="color: #E5E5E5; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.3rem;">No Geotagged Reports Found</div>
<div style="color: #888; font-size: 0.85rem;">Active complaints with GPS coordinates will appear on the interactive GIS map.</div>
</div>""",
            unsafe_allow_html=True
        )
        return

    # Center map on mean coordinates of reports
    center_lat = float(df["lat"].mean())
    center_lon = float(df["lon"].mean())

    layers = []

    # Layer 1: Scatterplot Layer with severity-coded pins
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["lon", "lat"],
        get_color=["color_r", "color_g", "color_b", "color_a"],
        get_radius="radius",
        radius_min_pixels=6,
        radius_max_pixels=25,
        pickable=True,
        auto_highlight=True
    )
    layers.append(scatter_layer)

    # Layer 2: Density / Heatmap Layer (if toggled)
    if show_heatmap:
        heat_layer = pdk.Layer(
            "HeatmapLayer",
            data=df,
            get_position=["lon", "lat"],
            get_weight="priority_score",
            radius_pixels=45,
            intensity=1.2,
            threshold=0.08
        )
        layers.append(heat_layer)

    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=12.2,
        pitch=30,
        bearing=0
    )

    tooltip = {
        "html": """
        <div style="font-family: sans-serif; font-size: 12px; padding: 4px; line-height: 1.4;">
            <div style="color: #C45D63; font-weight: 800; font-family: monospace; font-size: 13px;">{complaint_id}</div>
            <div style="color: #FFF; font-weight: 700; margin-bottom: 3px;">{category}</div>
            <div style="color: #CCC;"><b>Severity:</b> {severity} · <b>Priority:</b> {priority_score}/100</div>
            <div style="color: #999; margin-top: 3px; font-size: 11px;">📍 {location_text}</div>
            <div style="color: #60A5FA; margin-top: 2px;"><b>Status:</b> {status}</div>
        </div>
        """,
        "style": {
            "backgroundColor": "#050505",
            "color": "#E5E5E5",
            "border": "1px solid #222222",
            "borderRadius": "4px",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.5)"
        }
    }

    deck = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style="dark",
        tooltip=tooltip
    )

    st.pydeck_chart(deck, use_container_width=True, height=520)
