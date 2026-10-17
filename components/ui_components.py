"""
SmartCivic UI Components & Design System.
Incorporates modern animated UI tokens, glassmorphism, glowing micro-interactions,
and high-performance styling imported from wundercorp / awesome-components.
"""

import streamlit as st


def inject_custom_css():
    """
    Injects high-performance, GPU-accelerated design tokens and styles from the
    wundercorp / awesome-components library.
    Palette:
    - Primary dark canvas: #07090E, #0D121D, #131B2C
    - Glass cards: rgba(16, 23, 38, 0.75) with 16px blur
    - Accent primary: Civic Crimson / Rose (#E11D48 / #F43F5E)
    - Multimodal AI Accent: Indigo / Violet (#6366F1 / #A855F7)
    - Emerald Operational Accent: #10B981 / #34D399
    - Amber Warning / Triage Accent: #F59E0B / #FBBF24
    """
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

        :root {
            --bg-primary: #07090E;
            --bg-secondary: #0D121D;
            --bg-tertiary: #131B2C;
            --bg-card: rgba(16, 23, 38, 0.75);
            --bg-card-hover: rgba(23, 33, 54, 0.95);
            --bg-glass: rgba(14, 20, 33, 0.85);

            --border-subtle: rgba(255, 255, 255, 0.08);
            --border-visible: rgba(255, 255, 255, 0.14);
            --border-hover: rgba(99, 102, 241, 0.5);
            --border-focus: rgba(99, 102, 241, 0.8);
            --border-highlight: rgba(255, 255, 255, 0.22);

            --text-primary: #F8FAFC;
            --text-secondary: #94A3B8;
            --text-muted: #64748B;
            --text-dim: #475569;

            --accent-primary: #E11D48;
            --accent-primary-hover: #F43F5E;
            --accent-gradient: linear-gradient(135deg, #E11D48 0%, #BE123C 100%);
            --accent-ai-gradient: linear-gradient(135deg, #6366F1 0%, #A855F7 50%, #EC4899 100%);
            --accent-ai: #6366F1;
            --accent-emerald: #10B981;
            --accent-amber: #F59E0B;
            --accent-cyan: #06B6D4;

            --glow-primary: 0 0 25px rgba(225, 29, 72, 0.35);
            --glow-ai: 0 0 25px rgba(99, 102, 241, 0.35);
            --glow-emerald: 0 0 20px rgba(16, 185, 129, 0.3);
            --glow-card: 0 10px 30px rgba(0, 0, 0, 0.6);

            --font-display: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;

            --radius-sm: 8px;
            --radius-md: 12px;
            --radius-lg: 18px;
            --radius-full: 9999px;

            --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
            --transition-normal: 250ms cubic-bezier(0.4, 0, 0.2, 1);
            --transition-bounce: 350ms cubic-bezier(0.34, 1.56, 0.64, 1);
        }

        /* App Root with Subtle Ambient Mesh Glows */
        .stApp {
            background-color: var(--bg-primary) !important;
            background-image: 
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.12) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(225, 29, 72, 0.08) 0px, transparent 50%),
                radial-gradient(at 50% 50%, rgba(6, 182, 212, 0.04) 0px, transparent 60%) !important;
            background-attachment: fixed !important;
            color: var(--text-primary) !important;
            font-family: var(--font-body) !important;
        }

        /* Hide Streamlit Native Top Bar Header decoration */
        header[data-testid="stHeader"] {
            background-color: transparent !important;
        }

        /* Modern Glass Sidebar */
        section[data-testid="stSidebar"] {
            background-color: var(--bg-secondary) !important;
            border-right: 1px solid var(--border-subtle) !important;
            backdrop-filter: blur(16px) !important;
        }

        /* Main Container Spacing */
        .main .block-container {
            max-width: 1240px !important;
            padding-top: 1.2rem !important;
            padding-bottom: 4rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }

        /* ==========================================================================
           TOP NAVIGATION BRAND & CHIPS (from awesome-components brand-group)
           ========================================================================== */
        .nav-logo {
            font-family: var(--font-display);
            font-size: 1.12rem;
            font-weight: 800;
            letter-spacing: -0.01em;
            color: #FFFFFF;
            display: flex;
            align-items: center;
            gap: 0.65rem;
            height: 100%;
            padding-top: 0.25rem;
            text-transform: uppercase;
            white-space: nowrap !important;
            min-width: max-content !important;
        }

        .nav-logo-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--accent-primary);
            box-shadow: 0 0 14px var(--accent-primary), 0 0 6px var(--accent-primary-hover);
            display: inline-block;
            animation: pulseDot 2s infinite;
        }

        .nav-status-chip {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            font-size: 0.62rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 2px 7px;
            border-radius: var(--radius-full);
            background: rgba(16, 185, 129, 0.12);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.3);
            margin-left: 4px;
            white-space: nowrap !important;
        }

        .pulse-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #10B981;
            box-shadow: 0 0 8px #10B981;
            animation: pulseDot 1.6s infinite;
        }

        @keyframes pulseDot {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(0.85); }
        }

        /* ==========================================================================
           TOP NAVIGATION BAR & PILLS (from awesome-components nav-pills)
           ========================================================================== */
        div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-nav_btn_"]) {
            align-items: center !important;
            gap: 0.45rem !important;
            overflow-x: auto !important;
            overflow-y: hidden !important;
            flex-wrap: nowrap !important;
            scrollbar-width: none !important;
            -ms-overflow-style: none !important;
            padding: 0.25rem 0.1rem 0.5rem 0.1rem !important;
        }

        div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-nav_btn_"])::-webkit-scrollbar {
            display: none !important;
        }

        div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-nav_btn_"]) > div[data-testid="stColumn"] {
            min-width: max-content !important;
            flex: 1 0 auto !important;
        }

        div[class*="st-key-nav_btn_"] {
            width: 100% !important;
            min-width: max-content !important;
        }

        div[class*="st-key-nav_btn_"] > button {
            padding: 0.45rem 0.75rem !important;
            font-size: 0.82rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.01em !important;
            white-space: nowrap !important;
            word-break: keep-all !important;
            min-height: 2.25rem !important;
            height: 2.25rem !important;
            line-height: 1 !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
            border-radius: var(--radius-sm) !important;
        }

        div[class*="st-key-nav_btn_"] > button p,
        div[class*="st-key-nav_btn_"] > button div,
        div[class*="st-key-nav_btn_"] > button span {
            white-space: nowrap !important;
            word-break: keep-all !important;
            font-size: 0.82rem !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* ==========================================================================
           BUTTONS & MICRO-INTERACTIONS (from aliimam/button-soft-glow & app.css)
           ========================================================================== */
        .stButton > button {
            border-radius: var(--radius-md) !important;
            font-weight: 600 !important;
            letter-spacing: 0.02em !important;
            padding: 0.55rem 1.1rem !important;
            transition: all var(--transition-fast) !important;
            font-family: var(--font-body) !important;
            border: 1px solid transparent !important;
            font-size: 0.88rem !important;
            white-space: nowrap !important;
            word-break: keep-all !important;
        }

        .stButton > button p,
        .stButton > button div {
            white-space: nowrap !important;
            word-break: keep-all !important;
        }

        /* Primary Button: Vibrant Civic Crimson with Soft Glow */
        .stButton > button[kind="primary"] {
            background: var(--accent-gradient) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            box-shadow: 0 4px 18px rgba(225, 29, 72, 0.35) !important;
            position: relative !important;
        }

        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #F43F5E 0%, #E11D48 100%) !important;
            box-shadow: 0 6px 24px rgba(225, 29, 72, 0.55), 0 0 15px rgba(244, 63, 94, 0.4) !important;
            transform: translateY(-2px) !important;
            filter: brightness(1.1) !important;
        }

        .stButton > button[kind="primary"]:active {
            transform: translateY(0px) scale(0.98) !important;
        }

        /* Secondary Button: Glassmorphic Dark Slate with Subtle Hover Glow */
        .stButton > button[kind="secondary"] {
            background: var(--bg-card) !important;
            backdrop-filter: blur(12px) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border-subtle) !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4) !important;
        }

        .stButton > button[kind="secondary"]:hover {
            background: var(--bg-card-hover) !important;
            border-color: var(--border-hover) !important;
            color: #FFFFFF !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.6), 0 0 15px rgba(99, 102, 241, 0.25) !important;
            transform: translateY(-2px) !important;
        }

        .stButton > button[kind="secondary"]:active {
            transform: translateY(0px) scale(0.98) !important;
        }

        /* Download Button (from aliimam/button-border & app.css) */
        .stDownloadButton > button {
            border-radius: var(--radius-md) !important;
            background: linear-gradient(135deg, #4F46E5 0%, #3730A3 100%) !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            box-shadow: 0 4px 18px rgba(79, 70, 229, 0.35) !important;
            transition: all var(--transition-fast) !important;
            padding: 0.6rem 1.25rem !important;
        }

        .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
            box-shadow: 0 6px 24px rgba(99, 102, 241, 0.55) !important;
            transform: translateY(-2px) !important;
        }

        /* ==========================================================================
           FORM INPUTS & CONTROLS (from app.css search-input & custom-select)
           ========================================================================== */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div {
            background-color: var(--bg-secondary) !important;
            color: var(--text-primary) !important;
            border-radius: var(--radius-md) !important;
            border: 1px solid var(--border-subtle) !important;
            font-size: 0.92rem !important;
            transition: all var(--transition-normal) !important;
            backdrop-filter: blur(8px) !important;
        }

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        .stSelectbox > div > div:focus-within {
            border-color: var(--border-focus) !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.18), var(--glow-ai) !important;
            background-color: var(--bg-tertiary) !important;
        }

        .form-label-custom {
            font-family: var(--font-display);
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
        }

        /* File Uploader styling */
        .stFileUploader section {
            background-color: var(--bg-card) !important;
            border: 1px dashed var(--border-visible) !important;
            border-radius: var(--radius-md) !important;
            padding: 1.5rem !important;
            transition: all var(--transition-fast) !important;
        }

        .stFileUploader section:hover {
            border-color: var(--border-hover) !important;
            background-color: var(--bg-card-hover) !important;
            box-shadow: 0 0 15px rgba(99, 102, 241, 0.2) !important;
        }

        /* Camera input container */
        [data-testid="stCameraInput"] {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: var(--radius-md) !important;
            padding: 1rem !important;
        }

        /* ==========================================================================
           TYPOGRAPHY & HERO (from app.css Outfit typography & editorial tokens)
           ========================================================================== */
        .eyebrow {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: var(--accent-primary-hover);
            margin-bottom: 0.8rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .headline-hero {
            font-family: var(--font-display);
            font-size: 3.6rem;
            font-weight: 800;
            line-height: 1.08;
            letter-spacing: -0.035em;
            background: linear-gradient(135deg, #FFFFFF 40%, #A5B4FC 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1.1rem;
        }

        .headline-sub {
            font-size: 1.35rem;
            font-weight: 500;
            color: #CBD5E1;
            letter-spacing: -0.015em;
            margin-bottom: 1.2rem;
            line-height: 1.4;
        }

        .desc-editorial {
            font-size: 1.02rem;
            color: var(--text-secondary);
            line-height: 1.7;
            margin-bottom: 2.2rem;
            max-width: 92%;
        }

        .section-headline {
            font-family: var(--font-display);
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -0.025em;
            color: var(--text-primary);
            margin-bottom: 1.2rem;
            line-height: 1.2;
        }

        .editorial-divider {
            border: none;
            border-top: 1px solid var(--border-subtle);
            margin: 3.2rem 0;
        }

        /* ==========================================================================
           SYSTEM FLOW DIAGRAM (from aceternity/diagram-card & app.css)
           ========================================================================== */
        .diagram-container {
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            background: linear-gradient(135deg, rgba(16, 23, 38, 0.75) 0%, rgba(9, 13, 22, 0.9) 100%);
            backdrop-filter: blur(16px);
            padding: 1.75rem 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            box-shadow: var(--glow-card);
        }

        .diagram-eyebrow {
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 0.25rem;
            font-family: var(--font-display);
        }

        .diagram-node {
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            background: rgba(13, 18, 29, 0.75);
            padding: 0.85rem 1.1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all var(--transition-fast);
        }

        .diagram-node:hover {
            border-color: var(--border-hover);
            transform: translateX(4px);
            background: rgba(19, 27, 44, 0.85);
        }

        .diagram-node.active {
            border-color: var(--border-visible);
            background: rgba(19, 27, 44, 0.85);
        }

        .diagram-node-title {
            font-family: var(--font-display);
            font-size: 0.88rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            color: var(--text-primary);
        }

        .diagram-node-sub {
            font-size: 0.75rem;
            color: var(--text-secondary);
            margin-top: 0.2rem;
        }

        .diagram-arrow {
            text-align: center;
            font-size: 0.85rem;
            color: var(--text-muted);
            line-height: 1;
        }

        .diagram-badge {
            font-size: 0.66rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            color: #F43F5E;
            background: rgba(225, 29, 72, 0.12);
            border: 1px solid rgba(225, 29, 72, 0.3);
            border-radius: var(--radius-full);
            padding: 0.2rem 0.6rem;
        }

        .diagram-badge.active-ai {
            color: #A5B4FC;
            background: rgba(99, 102, 241, 0.15);
            border-color: rgba(99, 102, 241, 0.35);
            box-shadow: 0 0 10px rgba(99, 102, 241, 0.2);
        }

        /* ==========================================================================
           MUNICIPAL ANALYTICS KPI CARDS (from beratberkay/stat-card & stats-cards)
           ========================================================================== */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1.1rem;
            margin-bottom: 2rem;
        }

        .kpi-card {
            background: linear-gradient(135deg, rgba(16, 23, 38, 0.85) 0%, rgba(9, 13, 22, 0.95) 100%);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 1.35rem 1.45rem;
            position: relative;
            overflow: hidden;
            box-shadow: var(--glow-card);
            transition: all var(--transition-normal);
        }

        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #6366F1, #A855F7);
            opacity: 0.7;
        }

        .kpi-card:hover {
            transform: translateY(-3px);
            border-color: var(--border-hover);
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.7), 0 0 25px rgba(99, 102, 241, 0.2);
        }

        .kpi-card.accent-red::before { background: linear-gradient(90deg, #EF4444, #F43F5E); }
        .kpi-card.accent-amber::before { background: linear-gradient(90deg, #F59E0B, #F97316); }
        .kpi-card.accent-blue::before { background: linear-gradient(90deg, #3B82F6, #06B6D4); }
        .kpi-card.accent-green::before { background: linear-gradient(90deg, #10B981, #34D399); }
        .kpi-card.accent-purple::before { background: linear-gradient(90deg, #8B5CF6, #EC4899); }

        .kpi-label {
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 0.45rem;
            font-family: var(--font-display);
        }

        .kpi-number {
            font-size: 2.3rem;
            font-weight: 800;
            font-family: var(--font-display);
            color: #FFFFFF;
            line-height: 1.1;
            letter-spacing: -0.02em;
            text-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
        }

        .kpi-subtext {
            font-size: 0.75rem;
            color: var(--text-secondary);
            margin-top: 0.35rem;
        }

        /* ==========================================================================
           MULTIMODAL AI INTELLIGENCE CARD (from arunjdass/ai-agent-states & coss alert)
           ========================================================================== */
        .ai-result-card {
            border: 1px solid rgba(99, 102, 241, 0.35);
            background: linear-gradient(135deg, rgba(14, 20, 33, 0.9) 0%, rgba(8, 11, 19, 0.95) 100%);
            backdrop-filter: blur(16px);
            border-radius: var(--radius-lg);
            padding: 1.6rem;
            margin-top: 1rem;
            margin-bottom: 1.5rem;
            position: relative;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), 0 0 25px rgba(99, 102, 241, 0.15);
        }

        .ai-card-eyebrow {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.85rem;
        }

        .ai-card-label {
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #A5B4FC;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .ai-confidence-badge {
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            color: #34D399;
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.35);
            border-radius: var(--radius-full);
            padding: 3px 10px;
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);
        }

        .ai-category-title {
            font-family: var(--font-display);
            font-size: 1.6rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: #FFFFFF;
            margin-bottom: 0.9rem;
            line-height: 1.2;
        }

        .ai-detail-block {
            margin-top: 0.8rem;
            padding-top: 0.8rem;
            border-top: 1px solid var(--border-subtle);
        }

        .ai-field-label {
            font-size: 0.7rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 0.25rem;
        }

        .ai-field-value {
            font-size: 0.9rem;
            color: #E2E8F0;
            line-height: 1.5;
        }

        .ai-severity-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.76rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 4px 12px;
            border-radius: var(--radius-full);
            margin-top: 2px;
        }

        .severity-critical {
            color: #EF4444;
            background: rgba(239, 68, 68, 0.16);
            border: 1px solid rgba(239, 68, 68, 0.5);
            box-shadow: 0 0 12px rgba(239, 68, 68, 0.3);
        }

        .severity-high {
            color: #F97316;
            background: rgba(249, 115, 22, 0.16);
            border: 1px solid rgba(249, 115, 22, 0.5);
            box-shadow: 0 0 10px rgba(249, 115, 22, 0.2);
        }

        .severity-medium {
            color: #F59E0B;
            background: rgba(245, 158, 11, 0.14);
            border: 1px solid rgba(245, 158, 11, 0.4);
        }

        .severity-low {
            color: #10B981;
            background: rgba(16, 185, 129, 0.14);
            border: 1px solid rgba(16, 185, 129, 0.4);
        }

        .ai-priority-metric {
            display: flex;
            align-items: baseline;
            gap: 6px;
        }

        .ai-priority-val {
            font-size: 1.35rem;
            font-weight: 800;
            font-family: var(--font-mono);
            color: #FFFFFF;
        }

        .ai-priority-max {
            font-size: 0.78rem;
            color: var(--text-muted);
        }

        .ai-priority-bar-bg {
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.06);
            border-radius: var(--radius-full);
            margin-top: 6px;
            overflow: hidden;
        }

        .ai-priority-bar-fill {
            height: 100%;
            border-radius: var(--radius-full);
            transition: width 0.3s ease;
        }

        .ai-recommended-box {
            background: rgba(13, 18, 29, 0.85);
            border-left: 3px solid var(--accent-primary-hover);
            border-radius: 0 var(--radius-md) var(--radius-md) 0;
            border-top: 1px solid var(--border-subtle);
            border-right: 1px solid var(--border-subtle);
            border-bottom: 1px solid var(--border-subtle);
            padding: 0.9rem 1.1rem;
            margin-top: 0.5rem;
            font-size: 0.88rem;
            color: #F1F5F9;
            line-height: 1.45;
        }

        /* ==========================================================================
           LIFECYCLE PROGRESS STEPPER (from reui/stepper & nyxbui/stepper)
           ========================================================================== */
        .stepper-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: linear-gradient(135deg, rgba(16, 23, 38, 0.7) 0%, rgba(10, 14, 24, 0.85) 100%);
            backdrop-filter: blur(14px);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 1.3rem 1.8rem;
            margin: 1.3rem 0;
            position: relative;
            overflow-x: auto;
        }

        .stepper-step {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 7px;
            position: relative;
            flex: 1;
            text-align: center;
            z-index: 2;
        }

        .stepper-dot {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: #0E1524;
            border: 2px solid #28354D;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.72rem;
            font-weight: 800;
            color: var(--text-muted);
            transition: all var(--transition-bounce);
        }

        .stepper-step.active .stepper-dot {
            background: var(--accent-gradient);
            border-color: var(--accent-primary-hover);
            color: #FFFFFF;
            box-shadow: 0 0 15px rgba(225, 29, 72, 0.75);
            transform: scale(1.1);
        }

        .stepper-step.completed .stepper-dot {
            background: #10B981;
            border-color: #34D399;
            color: #061B12;
            box-shadow: 0 0 12px rgba(16, 185, 129, 0.4);
        }

        .stepper-label {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: var(--text-muted);
            transition: color var(--transition-fast);
        }

        .stepper-step.active .stepper-label {
            color: #FFFFFF;
            font-weight: 800;
        }

        .stepper-step.completed .stepper-label {
            color: #34D399;
        }

        .stepper-separator {
            flex: 1;
            height: 2px;
            background: rgba(255, 255, 255, 0.08);
            margin: 0 6px 18px 6px;
            transition: all var(--transition-normal);
        }

        .stepper-separator.completed {
            background: #10B981;
            box-shadow: 0 0 8px rgba(16, 185, 129, 0.4);
        }

        /* ==========================================================================
           DUPLICATE ALERT & GEOTAG BADGES (from coss.com alert & chetanverma alert)
           ========================================================================== */
        .duplicate-alert-banner {
            background: rgba(245, 158, 11, 0.1);
            border: 1px solid rgba(245, 158, 11, 0.35);
            border-left: 4px solid #F59E0B;
            border-radius: var(--radius-md);
            padding: 1.1rem 1.4rem;
            margin-bottom: 1.5rem;
            backdrop-filter: blur(12px);
            box-shadow: 0 8px 24px rgba(245, 158, 11, 0.12);
        }

        .geotag-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            padding: 4px 10px;
            border-radius: var(--radius-full);
            background: rgba(16, 185, 129, 0.15);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.35);
            margin-top: 5px;
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.15);
        }

        .geotag-badge-evidence {
            background: rgba(225, 29, 72, 0.15);
            color: #F43F5E;
            border: 1px solid rgba(225, 29, 72, 0.35);
            box-shadow: 0 0 10px rgba(225, 29, 72, 0.15);
        }

        /* ==========================================================================
           SLA GOVERNANCE & STATUS BADGES (from coss-badge & status-badge)
           ========================================================================== */
        .status-badge {
            display: inline-block;
            font-size: 0.7rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 3px 10px;
            font-family: var(--font-mono);
            border-radius: var(--radius-full);
        }

        .status-submitted {
            color: #60A5FA;
            background: rgba(59, 130, 246, 0.15);
            border: 1px solid rgba(59, 130, 246, 0.35);
        }

        .status-under_review {
            color: #C084FC;
            background: rgba(192, 132, 252, 0.15);
            border: 1px solid rgba(192, 132, 252, 0.35);
        }

        .status-assigned {
            color: #FBBF24;
            background: rgba(251, 191, 36, 0.15);
            border: 1px solid rgba(251, 191, 36, 0.35);
        }

        .status-in_progress {
            color: #FB923C;
            background: rgba(251, 146, 60, 0.15);
            border: 1px solid rgba(251, 146, 60, 0.35);
        }

        .status-resolved {
            color: #34D399;
            background: rgba(52, 211, 153, 0.15);
            border: 1px solid rgba(52, 211, 153, 0.35);
            box-shadow: 0 0 10px rgba(52, 211, 153, 0.2);
        }

        .status-rejected {
            color: #F87171;
            background: rgba(248, 113, 113, 0.15);
            border: 1px solid rgba(248, 113, 113, 0.35);
        }

        .sla-badge {
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 3px 9px;
            border-radius: var(--radius-full);
            display: inline-block;
            font-family: var(--font-mono);
        }

        .sla-ontrack {
            background: rgba(16, 185, 129, 0.15);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.4);
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);
        }

        .sla-expiring {
            background: rgba(245, 158, 11, 0.15);
            color: #FBBF24;
            border: 1px solid rgba(245, 158, 11, 0.4);
            box-shadow: 0 0 10px rgba(245, 158, 11, 0.2);
        }

        .sla-breached {
            background: rgba(239, 68, 68, 0.18);
            color: #F87171;
            border: 1px solid rgba(239, 68, 68, 0.45);
            box-shadow: 0 0 12px rgba(239, 68, 68, 0.25);
        }

        /* ==========================================================================
           TRIAGE QUEUE & TRACKING ROWS (from app.css component-card & timeline-rail)
           ========================================================================== */
        .triage-ticket-card {
            background: linear-gradient(135deg, rgba(16, 23, 38, 0.8) 0%, rgba(10, 14, 24, 0.9) 100%);
            backdrop-filter: blur(14px);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 1.5rem;
            margin-bottom: 1.2rem;
            border-left: 4px solid var(--border-visible);
            box-shadow: var(--glow-card);
            transition: all var(--transition-normal);
        }

        .triage-ticket-card:hover {
            transform: translateY(-2px);
            border-color: var(--border-hover);
            box-shadow: 0 14px 35px rgba(0, 0, 0, 0.7), 0 0 20px rgba(99, 102, 241, 0.15);
        }

        .triage-ticket-card.prio-critical {
            border-left-color: #EF4444;
            box-shadow: -4px 0 15px rgba(239, 68, 68, 0.3), var(--glow-card);
        }
        .triage-ticket-card.prio-high {
            border-left-color: #F97316;
            box-shadow: -4px 0 12px rgba(249, 115, 22, 0.25), var(--glow-card);
        }
        .triage-ticket-card.prio-medium { border-left-color: #F59E0B; }
        .triage-ticket-card.prio-low { border-left-color: #10B981; }

        .track-row {
            display: grid;
            grid-template-columns: 1.4fr 1.4fr 1.6fr 1fr 1fr 1fr;
            align-items: center;
            padding: 1.1rem 1.2rem;
            border-bottom: 1px solid var(--border-subtle);
            font-size: 0.9rem;
            color: var(--text-primary);
            transition: background var(--transition-fast);
        }

        .track-row:hover:not(.header) {
            background: rgba(19, 27, 44, 0.5);
        }

        .track-row.header {
            font-family: var(--font-display);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--text-muted);
            border-bottom: 1px solid var(--border-visible);
            background: var(--bg-secondary);
            border-radius: var(--radius-md) var(--radius-md) 0 0;
        }

        /* Success Submission Receipt */
        .success-card {
            border: 1px solid rgba(16, 185, 129, 0.35);
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(10, 15, 26, 0.95) 100%);
            backdrop-filter: blur(16px);
            border-radius: var(--radius-lg);
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 10px 35px rgba(0, 0, 0, 0.6), 0 0 25px rgba(16, 185, 129, 0.15);
        }

        .success-title {
            font-family: var(--font-display);
            font-size: 1.15rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            color: #34D399;
            margin-bottom: 0.6rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .success-desc {
            font-size: 1rem;
            color: var(--text-primary);
            line-height: 1.5;
            margin-bottom: 1.5rem;
        }

        .success-details-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1rem;
            background: rgba(13, 18, 29, 0.7);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 1.2rem;
            font-size: 0.88rem;
            color: #CBD5E1;
        }

        /* Analytics Distribution Bars */
        .analytics-dist-card {
            background: linear-gradient(135deg, rgba(16, 23, 38, 0.8) 0%, rgba(9, 13, 22, 0.9) 100%);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: var(--glow-card);
        }

        .analytics-dist-title {
            font-family: var(--font-display);
            font-size: 0.74rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 1.2rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border-subtle);
        }

        .analytics-bar-item {
            margin-bottom: 0.9rem;
        }

        .analytics-bar-header {
            display: flex;
            justify-content: space-between;
            font-size: 0.82rem;
            color: #E2E8F0;
            margin-bottom: 0.35rem;
        }

        .analytics-bar-track {
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.06);
            border-radius: var(--radius-full);
            overflow: hidden;
        }

        .analytics-bar-fill {
            height: 100%;
            background: var(--accent-primary-hover);
            border-radius: var(--radius-full);
            transition: width 0.3s ease;
        }

        /* Before & After Proof Card */
        .proof-comparison-card {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 1.2rem;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }

        .proof-badge {
            font-size: 0.65rem;
            font-weight: 800;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            padding: 3px 8px;
            border-radius: var(--radius-full);
        }

        .proof-before {
            background: rgba(225, 29, 72, 0.15);
            color: #F43F5E;
            border: 1px solid rgba(225, 29, 72, 0.35);
        }

        .proof-after {
            background: rgba(16, 185, 129, 0.15);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.35);
        }

        /* Timeline Items in About */
        .timeline-editorial-item {
            padding: 1.8rem 0;
            border-bottom: 1px solid var(--border-subtle);
        }

        .timeline-editorial-ver {
            font-size: 0.75rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--accent-primary-hover);
            margin-bottom: 0.35rem;
            font-family: var(--font-mono);
        }

        .timeline-editorial-title {
            font-family: var(--font-display);
            font-size: 1.35rem;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.015em;
            margin-bottom: 0.5rem;
        }

        .timeline-editorial-desc {
            font-size: 0.92rem;
            color: var(--text-secondary);
            line-height: 1.6;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
