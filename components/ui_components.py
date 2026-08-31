import streamlit as st


def inject_custom_css():
    """
    Injects minimal, editorial, dark technology design tokens.
    Palette: Near-black (#030303), warm off-white (#EBEBEB), muted gray (#888888),
    fine 1px borders (#1F1F1F), and restrained burgundy/civic red accent (#B15258).
    """
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

        :root {
            --bg-canvas: #030303;
            --bg-surface: #0A0A0A;
            --bg-elevated: #111111;
            --border-hairline: #1A1A1A;
            --border-visible: #262626;
            --border-highlight: #3A3A3A;
            --text-main: #EBEBEB;
            --text-muted: #888888;
            --text-dim: #555555;
            --accent-burgundy: #B15258;
            --accent-burgundy-light: #C45D63;
            --accent-burgundy-bg: rgba(177, 82, 88, 0.08);
            --accent-burgundy-border: rgba(177, 82, 88, 0.25);
            --status-submitted: #B15258;
        }

        /* App Root */
        .stApp {
            background-color: var(--bg-canvas) !important;
            color: var(--text-main) !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        /* Hide Streamlit Native Top Bar Header decoration */
        header[data-testid="stHeader"] {
            background-color: transparent !important;
        }

        /* Minimize sidebar chrome */
        section[data-testid="stSidebar"] {
            background-color: #060606 !important;
            border-right: 1px solid var(--border-hairline) !important;
        }

        /* Main Container Spacing */
        .main .block-container {
            max-width: 1120px !important;
            padding-top: 1.5rem !important;
            padding-bottom: 4rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }

        /* Top Navigation Bar Brand */
        .nav-logo {
            font-size: 1.05rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            color: var(--text-main);
            text-transform: uppercase;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            height: 100%;
            padding-top: 0.4rem;
        }

        .nav-logo-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background-color: var(--accent-burgundy);
            display: inline-block;
        }

        /* Eyebrow Text */
        .eyebrow {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: var(--accent-burgundy);
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        /* Editorial Headlines */
        .headline-hero {
            font-size: 3.8rem;
            font-weight: 800;
            line-height: 1.08;
            letter-spacing: -0.04em;
            color: var(--text-main);
            margin-bottom: 1.2rem;
        }

        .headline-sub {
            font-size: 1.4rem;
            font-weight: 500;
            color: #C8C8C8;
            letter-spacing: -0.02em;
            margin-bottom: 1.2rem;
            line-height: 1.35;
        }

        .desc-editorial {
            font-size: 1.05rem;
            color: var(--text-muted);
            line-height: 1.7;
            margin-bottom: 2.2rem;
            max-width: 90%;
        }

        /* Hero Diagram */
        .diagram-container {
            border: 1px solid var(--border-visible);
            background: #080808;
            padding: 1.75rem 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .diagram-eyebrow {
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: var(--text-dim);
            margin-bottom: 0.25rem;
        }

        .diagram-node {
            border: 1px solid var(--border-hairline);
            background: #050505;
            padding: 0.85rem 1.1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .diagram-node.active {
            border-color: var(--border-visible);
            background: #0C0C0C;
        }

        .diagram-node-title {
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            color: var(--text-main);
        }

        .diagram-node-sub {
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 0.15rem;
        }

        .diagram-arrow {
            text-align: center;
            font-size: 0.8rem;
            color: #444444;
            line-height: 1;
        }

        .diagram-badge {
            font-size: 0.65rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            color: var(--accent-burgundy-light);
            background: var(--accent-burgundy-bg);
            border: 1px solid var(--accent-burgundy-border);
            padding: 0.2rem 0.5rem;
        }

        .diagram-badge.active-ai {
            color: #10B981;
            background: rgba(16, 185, 129, 0.1);
            border-color: rgba(16, 185, 129, 0.3);
        }

        /* Section Headings */
        .section-headline {
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            color: var(--text-main);
            margin-bottom: 1.5rem;
            line-height: 1.2;
        }

        /* Editorial Dividers */
        .editorial-divider {
            border: none;
            border-top: 1px solid var(--border-hairline);
            margin: 3.5rem 0;
        }

        /* Form Labels & Overrides */
        .form-label-custom {
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--text-dim);
            margin-bottom: 0.5rem;
        }

        /* Custom UI Buttons */
        .stButton > button {
            border-radius: 0px !important;
            font-weight: 600 !important;
            letter-spacing: 0.02em !important;
            padding: 0.6rem 1.2rem !important;
            transition: all 0.15s ease !important;
        }

        .stButton > button[kind="primary"] {
            background-color: var(--accent-burgundy) !important;
            color: #FFFFFF !important;
            border: 1px solid var(--accent-burgundy) !important;
        }

        .stButton > button[kind="primary"]:hover {
            background-color: var(--accent-burgundy-light) !important;
            border-color: var(--accent-burgundy-light) !important;
            box-shadow: none !important;
        }

        .stButton > button[kind="secondary"] {
            background-color: transparent !important;
            color: var(--text-main) !important;
            border: 1px solid var(--border-highlight) !important;
        }

        .stButton > button[kind="secondary"]:hover {
            border-color: var(--text-main) !important;
            color: #FFFFFF !important;
            background-color: #0E0E0E !important;
        }

        /* Input Controls Overrides */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div {
            background-color: #080808 !important;
            color: var(--text-main) !important;
            border-radius: 0px !important;
            border: 1px solid var(--border-visible) !important;
            font-size: 0.92rem !important;
        }

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: var(--accent-burgundy) !important;
            box-shadow: none !important;
        }

        /* GPS Location Box */
        .gps-detected-box {
            border: 1px solid var(--border-visible);
            background: #080808;
            padding: 1.1rem 1.2rem;
            margin: 0.8rem 0;
        }

        .gps-detected-title {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #10B981;
            margin-bottom: 0.35rem;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .gps-detected-address {
            font-size: 0.92rem;
            color: var(--text-main);
            line-height: 1.4;
            margin-bottom: 0.35rem;
        }

        .gps-detected-coords {
            font-size: 0.78rem;
            font-family: monospace;
            color: var(--accent-burgundy-light);
        }

        /* AI Result Card */
        .ai-result-card {
            border: 1px solid var(--border-visible);
            background: #090909;
            padding: 1.5rem;
            margin-top: 1rem;
            margin-bottom: 1.5rem;
            position: relative;
        }

        .ai-card-eyebrow {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.8rem;
        }

        .ai-card-label {
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--accent-burgundy-light);
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .ai-confidence-badge {
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            color: #10B981;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.25);
            padding: 2px 8px;
        }

        .ai-category-title {
            font-size: 1.5rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: var(--text-main);
            margin-bottom: 0.9rem;
            line-height: 1.2;
        }

        .ai-detail-block {
            margin-top: 0.8rem;
            padding-top: 0.8rem;
            border-top: 1px solid var(--border-hairline);
        }

        .ai-field-label {
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--text-dim);
            margin-bottom: 0.25rem;
        }

        .ai-field-value {
            font-size: 0.88rem;
            color: #D4D4D4;
            line-height: 1.5;
        }

        /* AI Risk Assessment Card Section */
        .ai-risk-divider {
            margin-top: 1.2rem;
            margin-bottom: 1.0rem;
            border: none;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
        }

        .ai-risk-header {
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #A3A3A3;
            margin-bottom: 0.9rem;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .ai-risk-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.0rem;
            margin-bottom: 0.9rem;
        }

        .ai-severity-badge {
            display: inline-block;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 3px 10px;
            margin-top: 2px;
        }

        .severity-low {
            color: #10B981;
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .severity-medium {
            color: #F59E0B;
            background: rgba(245, 158, 11, 0.12);
            border: 1px solid rgba(245, 158, 11, 0.3);
        }

        .severity-high {
            color: #F97316;
            background: rgba(249, 115, 22, 0.15);
            border: 1px solid rgba(249, 115, 22, 0.4);
        }

        .severity-critical {
            color: #EF4444;
            background: rgba(239, 68, 68, 0.18);
            border: 1px solid rgba(239, 68, 68, 0.5);
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.2);
        }

        .ai-priority-metric {
            display: flex;
            align-items: baseline;
            gap: 6px;
        }

        .ai-priority-val {
            font-size: 1.3rem;
            font-weight: 800;
            font-family: monospace;
            color: #EBEBEB;
        }

        .ai-priority-max {
            font-size: 0.78rem;
            color: #777;
        }

        .ai-priority-bar-bg {
            width: 100%;
            height: 4px;
            background: #1C1C1C;
            margin-top: 6px;
            overflow: hidden;
        }

        .ai-priority-bar-fill {
            height: 100%;
            transition: width 0.3s ease;
        }

        .ai-risk-factors-list {
            margin: 0.4rem 0 0.2rem 0;
            padding-left: 1.2rem;
            list-style-type: square;
        }

        .ai-risk-factor-item {
            font-size: 0.84rem;
            color: #CCCCCC;
            line-height: 1.5;
            margin-bottom: 3px;
        }

        .ai-recommended-box {
            background: #0D0D0D;
            border-left: 3px solid var(--accent-burgundy-light);
            border-top: 1px solid var(--border-hairline);
            border-right: 1px solid var(--border-hairline);
            border-bottom: 1px solid var(--border-hairline);
            padding: 0.8rem 1rem;
            margin-top: 0.4rem;
            font-size: 0.88rem;
            color: #E5E5E5;
            line-height: 1.45;
        }

        /* 5-Step Process Sequence */
        .sequence-item {
            padding: 1.4rem 0;
            border-bottom: 1px solid var(--border-hairline);
        }

        .sequence-header {
            display: flex;
            align-items: baseline;
            gap: 1.2rem;
            margin-bottom: 0.3rem;
        }

        .sequence-num {
            font-size: 1.1rem;
            font-weight: 800;
            color: var(--accent-burgundy);
            font-family: monospace;
        }

        .sequence-title {
            font-size: 1.15rem;
            font-weight: 700;
            letter-spacing: -0.01em;
            color: var(--text-main);
        }

        .sequence-desc {
            font-size: 0.88rem;
            color: var(--text-muted);
            margin-left: 2.3rem;
            line-height: 1.5;
        }

        /* Progress Step Indicator in Form */
        .progress-indicator-bar {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border-hairline);
        }

        .progress-step-pill {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            color: var(--text-dim);
            text-transform: uppercase;
        }

        .progress-step-pill.active {
            color: var(--accent-burgundy-light);
        }

        /* Receipt / Ticket */
        .receipt-ticket {
            border: 1px solid var(--border-visible);
            background: #080808;
            padding: 2.5rem;
            margin-bottom: 2rem;
            position: relative;
        }

        .receipt-ticket-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid var(--border-hairline);
            margin-bottom: 1.8rem;
        }

        .receipt-ticket-title {
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            color: var(--text-main);
        }

        .receipt-ticket-code {
            font-family: monospace;
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            color: var(--accent-burgundy-light);
            margin-top: 0.4rem;
        }

        .receipt-ticket-status {
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--accent-burgundy-light);
            background: var(--accent-burgundy-bg);
            border: 1px solid var(--accent-burgundy-border);
            padding: 0.35rem 0.8rem;
        }

        .receipt-detail-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.8rem;
            margin-bottom: 1.8rem;
        }

        .receipt-detail-label {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--text-dim);
            margin-bottom: 0.3rem;
        }

        .receipt-detail-val {
            font-size: 0.98rem;
            color: var(--text-main);
            font-weight: 500;
        }

        /* Tracking Table Rows */
        .track-row {
            display: grid;
            grid-template-columns: 1.4fr 1.4fr 1.6fr 1fr 1fr 1fr;
            align-items: center;
            padding: 1.1rem 1rem;
            border-bottom: 1px solid var(--border-hairline);
            font-size: 0.9rem;
            color: var(--text-main);
        }

        .track-row.header {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--text-dim);
            border-bottom: 1px solid var(--border-visible);
            background: #050505;
        }

        /* Timeline Items in About */
        .timeline-editorial-item {
            padding: 1.8rem 0;
            border-bottom: 1px solid var(--border-hairline);
        }

        .timeline-editorial-ver {
            font-size: 0.75rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--accent-burgundy);
            margin-bottom: 0.35rem;
        }

        .timeline-editorial-title {
            font-size: 1.3rem;
            font-weight: 700;
            color: var(--text-main);
            letter-spacing: -0.02em;
            margin-bottom: 0.5rem;
        }

        .timeline-editorial-desc {
            font-size: 0.9rem;
            color: var(--text-muted);
            line-height: 1.6;
        }

        /* v0.4 Municipal Analytics KPI Cards */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .kpi-card {
            background: #080808;
            border: 1px solid var(--border-visible);
            padding: 1.2rem 1.4rem;
            border-top: 3px solid var(--border-highlight);
            position: relative;
        }

        .kpi-card.accent-red { border-top-color: #EF4444; }
        .kpi-card.accent-amber { border-top-color: #F59E0B; }
        .kpi-card.accent-blue { border-top-color: #3B82F6; }
        .kpi-card.accent-green { border-top-color: #10B981; }
        .kpi-card.accent-purple { border-top-color: #8B5CF6; }

        .kpi-label {
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--text-dim);
            margin-bottom: 0.4rem;
        }

        .kpi-number {
            font-size: 2.2rem;
            font-weight: 800;
            font-family: monospace;
            color: var(--text-main);
            line-height: 1.1;
        }

        .kpi-subtext {
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 0.3rem;
        }

        /* Status Badges */
        .status-badge {
            display: inline-block;
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 2px 8px;
            font-family: monospace;
        }

        .status-submitted {
            color: #60A5FA;
            background: rgba(59, 130, 246, 0.12);
            border: 1px solid rgba(59, 130, 246, 0.3);
        }

        .status-under_review {
            color: #C084FC;
            background: rgba(192, 132, 252, 0.12);
            border: 1px solid rgba(192, 132, 252, 0.3);
        }

        .status-assigned {
            color: #FBBF24;
            background: rgba(251, 191, 36, 0.12);
            border: 1px solid rgba(251, 191, 36, 0.3);
        }

        .status-in_progress {
            color: #FB923C;
            background: rgba(251, 146, 60, 0.12);
            border: 1px solid rgba(251, 146, 60, 0.3);
        }

        .status-resolved {
            color: #34D399;
            background: rgba(52, 211, 153, 0.12);
            border: 1px solid rgba(52, 211, 153, 0.3);
        }

        .status-rejected {
            color: #F87171;
            background: rgba(248, 113, 113, 0.12);
            border: 1px solid rgba(248, 113, 113, 0.3);
        }

        /* Lifecycle Progress Stepper */
        .stepper-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #050505;
            border: 1px solid var(--border-hairline);
            padding: 1.2rem 1.5rem;
            margin: 1.2rem 0;
            overflow-x: auto;
        }

        .stepper-step {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
            position: relative;
            flex: 1;
            text-align: center;
        }

        .stepper-dot {
            width: 22px;
            height: 22px;
            border-radius: 50%;
            background: #141414;
            border: 2px solid #333333;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.65rem;
            font-weight: 800;
            color: #777;
            z-index: 2;
        }

        .stepper-step.active .stepper-dot {
            background: var(--accent-burgundy);
            border-color: var(--accent-burgundy-light);
            color: #FFF;
            box-shadow: 0 0 8px rgba(177, 82, 88, 0.6);
        }

        .stepper-step.completed .stepper-dot {
            background: #10B981;
            border-color: #10B981;
            color: #000;
        }

        .stepper-label {
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: #666;
        }

        .stepper-step.active .stepper-label { color: #EBEBEB; }
        .stepper-step.completed .stepper-label { color: #10B981; }

        /* Analytics Distribution Bars */
        .analytics-dist-card {
            background: #080808;
            border: 1px solid var(--border-visible);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }

        .analytics-dist-title {
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--text-dim);
            margin-bottom: 1.2rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border-hairline);
        }

        .analytics-bar-item {
            margin-bottom: 0.85rem;
        }

        .analytics-bar-header {
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: #D4D4D4;
            margin-bottom: 0.25rem;
        }

        .analytics-bar-track {
            width: 100%;
            height: 6px;
            background: #141414;
            border-radius: 0px;
            overflow: hidden;
        }

        .analytics-bar-fill {
            height: 100%;
            background: var(--accent-burgundy-light);
            transition: width 0.3s ease;
        }

        /* Triage Queue Row & Card */
        .triage-ticket-card {
            background: #080808;
            border: 1px solid var(--border-visible);
            padding: 1.4rem;
            margin-bottom: 1.2rem;
            border-left: 3px solid var(--border-highlight);
        }

        .triage-ticket-card.prio-critical { border-left-color: #EF4444; }
        .triage-ticket-card.prio-high { border-left-color: #F97316; }
        .triage-ticket-card.prio-medium { border-left-color: #F59E0B; }
        .triage-ticket-card.prio-low { border-left-color: #10B981; }

        /* SLA Governance Badges */
        .sla-badge {
            font-size: 0.65rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 2px 8px;
            border-radius: 2px;
            display: inline-block;
        }

        .sla-ontrack {
            background: rgba(16, 185, 129, 0.12);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .sla-expiring {
            background: rgba(245, 158, 11, 0.12);
            color: #FBBF24;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }

        .sla-breached {
            background: rgba(239, 68, 68, 0.15);
            color: #F87171;
            border: 1px solid rgba(239, 68, 68, 0.4);
        }

        /* Before & After Proof Card */
        .proof-comparison-card {
            background: #060606;
            border: 1px solid #1F1F1F;
            padding: 1.2rem;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }

        .proof-badge {
            font-size: 0.65rem;
            font-weight: 800;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            padding: 2px 7px;
            border-radius: 2px;
        }

        .proof-before {
            background: rgba(196, 93, 99, 0.15);
            color: #E2848A;
            border: 1px solid rgba(196, 93, 99, 0.3);
        }

        .proof-after {
            background: rgba(16, 185, 129, 0.15);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        /* Duplicate Alert Banner */
        .duplicate-alert-banner {
            background: rgba(245, 158, 11, 0.08);
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-left: 3px solid #F59E0B;
            padding: 1rem 1.2rem;
            margin-bottom: 1.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

