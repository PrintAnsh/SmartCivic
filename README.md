# SmartCivic

**Smart Civic Technology Platform**

SmartCivic is a modern civic technology platform designed to streamline civic issue reporting and create a high-trust foundation for intelligent problem analysis, location-aware routing, persistent lifecycle tracking, and municipal governance analytics.

---

## Current Version: v0.4 — Complaint Management & Municipal Analytics

Version 0.4 upgrades SmartCivic into a full-lifecycle municipal operations platform featuring **Persistent JSON Storage**, **Complaint Status Lifecycles**, **Enhanced Citizen Tracking with Visual Steppers**, and an **Interactive Municipal Governance & Analytics Dashboard**.

### Core Features in v0.4

- 💾 **Persistent Complaint & Evidence Storage (`utils/storage.py`)**:
  - Complaints and status audit histories persist atomically to `data/complaints.json`.
  - Evidence images saved and served from `data/images/{complaint_id}.jpg`.
  - Zero external database complexity; survives server restarts and browser reloads.
  - Built-in demo data generator for instant testing on fresh setups.

- 🔄 **Municipal Status Lifecycle Workflow**:
  - Full 6-state municipal lifecycle: `SUBMITTED` → `UNDER_REVIEW` → `ASSIGNED` → `IN_PROGRESS` → `RESOLVED` / `REJECTED`.
  - Complete transition audit trail (`status_history`) recording timestamps and operational notes.
  - Department routing across 7 municipal divisions (*Public Works*, *Sanitation*, *Electrical*, *Water Supply*, *Drainage*, *Parks*, *Administration*).

- 🔍 **Enhanced Citizen Verification & Tracking (`Track` Page)**:
  - Instant search by Reference Code (`SC-2026-XXXXXX`), address, or keyword.
  - Category and Status filter dropdowns.
  - **Visual 5-Step Progress Stepper** (`Submitted` → `Under Review` → `Assigned` → `In Progress` → `Resolved`).
  - Expandable detailed ticket cards featuring attached photos, full AI triage breakdown, GPS coordinates with Google Maps links, and complete transition history.

- 📊 **Municipal Governance & Analytics Dashboard (`Analytics & Triage` Page)**:
  - **Real-Time KPI Summary Cards**: Total Logged, Pending Review, In Progress, Resolved, Critical/Urgent Count, and Average Urgency Score.
  - **Data Intelligence Distribution Breakdown**:
    - Reports by Civic Category distribution bars.
    - Reports by Severity Tier breakdown.
    - Lifecycle Status distribution.
    - Workload by Municipal Department.
  - **Priority-Sorted Triage Queue**:
    - Highest priority score and critical severity issues automatically float to the top.
    - Filter queue by Status, Severity, and Department.
    - Inline interactive municipal action panels to update status, assign departments, and record resolution notes with immediate JSON persistence.

- 🤖 **Unified Multimodal AI Vision & Triage (`ai/`)**:
  - Single unified Gemini Vision call returning Category, Confidence, Severity (`Low`/`Medium`/`High`/`Critical`), Priority Score (`0–100`), Risk Factors, and Recommended Action.
  - Pydantic schema validation and deterministic fallback sanitization.

- 📷 **Dual-Mode Visual Evidence & 📍 Geolocation**:
  - Native browser camera capture or device image upload.
  - HTML5 browser GPS detection with multi-provider reverse geocoding auto-fill.

---

## AI Configuration (Google GenAI)

SmartCivic uses the official `google-genai` SDK. Configure your API key using one of the two standard methods:

### Option 1: Streamlit Secrets (Recommended for local dev & Streamlit Cloud)
Create `.streamlit/secrets.toml` in the project root:

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
```

*(Note: `.streamlit/secrets.toml` is included in `.gitignore` and is never committed).*

### Option 2: Environment Variable
Set the environment variable in your terminal:

```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your_gemini_api_key_here"

# Linux / macOS
export GEMINI_API_KEY="your_gemini_api_key_here"
```

---

## Technology Stack

- **Language**: Python 3.10+
- **Frontend Framework**: Streamlit
- **AI / Multimodal Vision**: Google GenAI SDK (`google-genai`) with Pydantic schema validation
- **Image Processing**: Pillow (PIL)
- **Geolocation & Mapping**: HTML5 Geolocation API + OpenStreetMap Nominatim Reverse Geocoding
- **Storage Layer**: Atomic JSON Store (`data/complaints.json`) & Image Directory (`data/images/`)
- **Styling**: Modular CSS Tokens & Editorial Dark Design System

---

## Getting Started

### Installation

1. Navigate to the project directory:
   ```bash
   cd SIH-SmartCivic
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

Launch the SmartCivic application:

```bash
python -m streamlit run app.py
```

### Running the Diagnostic Tool

Run the automated diagnostic script to verify environment, API key, model availability, and reverse geocoding:

```bash
python scratch/diagnose_gemini.py
```

---

## License

Developed for the Smart India Hackathon (SIH) — Smart Civic Technology Initiative.
