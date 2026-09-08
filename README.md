# SMARTCIVIC

**Report. Understand. Route. Resolve.**

SmartCivic is an intelligent civic technology platform engineered to modernize public infrastructure reporting. Moving beyond traditional complaint portals that merely record and forward text, SmartCivic introduces an automated intelligence layer that analyzes visual evidence using multimodal AI, calculates dynamic priority urgency, clusters duplicate reports within geographic proximity, assigns responsible municipal departments, and tracks resolution through verifiable Before/After evidence.

> **Smart India Hackathon 2026**  
> **Project:** Smart Civic Issue Reporting Platform   
> **Core Message:** *“Every civic issue deserves the right attention, from the right department, at the right time.”*

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Key Features](#2-key-features)
3. [How SmartCivic Works](#3-how-smartcivic-works)
4. [AI Pipeline & Visual Triage](#4-ai-pipeline--visual-triage)
5. [Priority & Severity Assessment System](#5-priority--severity-assessment-system)
6. [Proximity-Based Duplicate Detection](#6-proximity-based-duplicate-detection)
7. [Geospatial Intelligence & GIS Map](#7-geospatial-intelligence--gis-map)
8. [Complaint Lifecycle & SLA Governance](#8-complaint-lifecycle--sla-governance)
9. [Technology Stack](#9-technology-stack)
10. [Current Prototype vs. Proposed Production Architecture](#10-current-prototype-vs-proposed-production-architecture)
11. [Project Structure](#11-project-structure)
12. [Installation & Setup](#12-installation--setup)
13. [Running the Application](#13-running-the-application)
14. [Google Gemini API Configuration](#14-google-gemini-api-configuration)
15. [Automated Testing & Diagnostics](#15-automated-testing--diagnostics)
16. [Deployment](#16-deployment)
17. [Security & Secrets Management](#17-security--secrets-management)
18. [Current Prototype Limitations](#18-current-prototype-limitations)
19. [Future Roadmap](#19-future-roadmap)
20. [Why SmartCivic?](#20-why-smartcivic)
21. [End-to-End Use Case Walkthrough](#21-end-to-end-use-case-walkthrough)
22. [Smart India Hackathon 2026 Team](#22-smart-india-hackathon-2026-team)
23. [Research & Industry References](#23-research--industry-references)
24. [Development Status](#24-development-status)
25. [License](#25-license)

---

## 1. Project Overview

### The Problem
Urban local bodies and municipal corporations receive thousands of citizen complaints each month concerning potholes, broken streetlights, water pipeline leaks, overflowing garbage bins, and clogged drainage networks. Traditional grievance portals suffer from critical operational bottlenecks:
- **Unstructured Intake:** Citizens submit ambiguous, subjective text descriptions without standardized categorization.
- **Triage Overload:** Municipal officers must manually inspect, classify, and evaluate thousands of incoming complaints without objective severity scoring.
- **Redundant Workload:** A single visible issue (e.g., a major road pothole) frequently triggers dozens of separate complaints, generating duplicate tickets, conflicting field dispatches, and wasted public resources.
- **Lack of Verification:** Citizens have minimal transparency regarding turnaround times, and municipalities lack structured mechanisms to record verifiable proof of repair.

### The SmartCivic Solution
SmartCivic integrates multimodal artificial intelligence and spatial intelligence directly into the intake pipeline:

```
[ CITIZEN REPORT ]
       │
       ▼
[ 1. UNDERSTAND ] ── Multimodal Gemini Vision classifies category & identifies visible hazards
       │
       ▼
[ 2. PRIORITIZE ] ── Calculates objective 0–100 urgency score & assigns SLA deadline
       │
       ▼
[ 3. DEDUPLICATE ] ── Spherical Haversine clustering identifies active nearby tickets (<75m)
       │
       ▼
[ 4. ROUTE ] ────── Automated department routing to specialized municipal divisions
       │
       ▼
[ 5. RESOLVE ] ──── Verifiable Before & After photographic evidence + status audit trail
```

---

## 2. Key Features

The following features are **fully implemented and verified** in the current codebase:

- **Dual-Mode Visual Evidence Intake**: Citizens can capture live photos using their device camera or upload image files (JPG, PNG).
- **Multimodal AI Vision Classification**: Integrates the official `google-genai` SDK to classify images into a standardized 7-category municipal taxonomy.
- **AI Confidence Scoring**: Evaluates visual confidence with qualitative indicators (`High`, `Medium`, `Low`) and numerical percentages.
- **Automated Severity Triage**: Evaluates physical risk to determine severity tier (`Critical`, `High`, `Medium`, `Low`).
- **Dynamic Priority Scoring (0–100)**: Generates a granular numerical urgency score mapped to severity tiers to rank field work orders.
- **Risk-Factor Extraction**: Automatically extracts 1 to 5 concise, observable hazard factors (e.g., *"Vehicle safety risk"*, *"Accident hazard at night"*).
- **Recommended Municipal Action**: Generates actionable, concise field instructions (e.g., *"Inspect roadway base and patch pothole asphalt surface"*).
- **Structured Pydantic Validation**: Validates AI inference results against strict schemas with deterministic fallback sanitization.
- **HTML5 Browser GPS Geolocation**: Custom bidirectional Streamlit component capturing high-accuracy latitude and longitude coordinates.
- **Multi-Provider Reverse Geocoding**: Translates GPS coordinates into human-readable street addresses via OpenStreetMap Nominatim with BigDataCloud fallback.
- **Proximity-Based Duplicate Detection**: Uses the spherical Haversine formula to detect active complaints within a 75-meter radius and presents warning alerts.
- **Automated Department Routing**: Automatically routes reports to 7 specialized municipal divisions based on category.
- **Unique Ticket Generation**: Generates standardized municipal complaint codes formatted as `SC-{YEAR}-{RANDOM_6_DIGITS}` (e.g., `SC-2026-483921`).
- **Comprehensive Ticket Tracking**: Searchable citizen tracking dashboard filtering by Ticket ID, address, keyword, status, and category.
- **Visual 5-Step Lifecycle Stepper**: Dynamic progress stepper visualizing real ticket transitions: `Submitted` → `Under Review` → `Assigned` → `In Progress` → `Resolved` (or `Rejected`).
- **Status Audit Trail**: Complete immutable operational history logging every status change with exact timestamps and notes.
- **SLA Turnaround Engine**: Dynamic service level agreement targets (24h for Critical, 48h for High, 72h for Medium, 168h for Low) with live breach countdowns.
- **Field Resolution Evidence**: Side-by-side photographic verification comparing citizen "Before" photos against municipal field crew "After" repair photos.
- **Interactive GIS Map**: PyDeck WebGL map visualization rendering geotagged incidents with radius-scaled, severity-colored pins.
- **Density Heatmap Layer**: Toggleable spatial heatmap layer weighted by incident priority score.
- **Municipal Analytics Dashboard**: Real-time KPI metric cards (Total Logged, Active, High Priority, Resolved, SLA Compliance).
- **Workload Distribution Visualizations**: Statistical progress bars displaying distributions across categories, severities, lifecycles, and departments.
- **Priority-Ranked Triage Queue**: Operations queue automatically sorting tickets with highest priority and critical severity at the top.
- **Interactive Triage Panels**: Municipal controls to reassign departments, transition statuses, enter notes, and upload resolution proof photos.
- **RFC 4180 CSV Export**: One-click generation and download of complete incident logs for external analysis.
- **Printable Field Dispatch Brief**: Markdown-formatted work-order dispatch sheet ready for printing or field crew distribution.
- **Atomic Local Persistence**: Local JSON storage (`data/complaints.json`) with safe atomic write-replace cycles and image directory persistence (`data/images/`).

---

## 3. How SmartCivic Works

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CITIZEN INTAKE STAGE                              │
│  Citizen captures photo via camera or file upload + detects browser GPS.    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MULTIMODAL AI TRIAGE                                │
│  Google Gemini Vision analyzes image → Classifies category (Pothole, etc.)  │
│  → Assesses severity tier & priority score (0-100) → Extracts risk factors. │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SPATIAL INTELLIGENCE & DEDUPLICATION                     │
│  Coordinates reverse-geocoded to street address. Haversine check scans for   │
│  matching active reports within 75m to prevent duplicate municipal dispatch.│
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      MUNICIPAL OPERATIONS & DISPATCH                        │
│  Ticket auto-assigned to department. Floats to top of Triage Queue by       │
│  priority. SLA countdown timer initiates (24h–168h target).                 │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     RESOLUTION & VERIFIABLE PROOF                           │
│  Field crew executes repair → Uploads "After" photo → Marks ticket Resolved.│
│  Citizen inspects Before vs. After proof on tracking portal.                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. AI Pipeline & Visual Triage

SmartCivic utilizes the official Google GenAI SDK (`google-genai`) to run multimodal vision inference on citizen-submitted photographs.

```
Citizen Photo (PIL / JPEG) ──► google-genai Client ──► Gemini Multimodal Model
                                                              │
   ┌──────────────────────────────────────────────────────────┘
   ▼
Raw JSON Response
   │
   ▼
Pydantic Validation (CivicClassificationResult)
   ├── category:            Civic category from standardized 7-item taxonomy
   ├── confidence:          Numerical confidence score (0.0 to 1.0)
   ├── confidence_level:    Qualitative rating ("High", "Medium", "Low")
   ├── reason:              1 factual sentence on physical evidence observed
   ├── summary:             1-2 sentence problem summary
   ├── severity:            "Low" | "Medium" | "High" | "Critical"
   ├── priority_score:      Integer (0 to 100)
   ├── risk_factors:        1 to 5 concise hazard statements
   └── recommended_action:  Concise field maintenance advice
```

### Clarification on Machine Learning Architecture
- **Current Implementation:** SmartCivic currently leverages Google Gemini multimodal vision through the `google-genai` SDK for zero-shot visual classification, risk assessment, and reasoning.
- **Proposed Future Architecture:** A local custom-trained computer vision model (e.g., YOLOv8 / MobileNet) running on-device or on edge servers for offline detection, supplemented by multimodal LLMs for complex policy routing.

### Resilient Fallback & Sanitization Handling
The AI engine (`ai/issue_classifier.py`) implements deterministic safety fallbacks:
- If severity is missing or invalid, it defaults to `"Medium"`.
- Priority scores are strictly clamped between `0` and `100`.
- Unrecognized categories default to `"Other / Unclear"`.
- Empty risk factors are populated with safe contextual defaults.
- Hard timeouts (12.0 seconds) prevent thread hangs on slow connections.

---

## 5. Priority & Severity Assessment System

SmartCivic does not rely on subjective citizen urgency claims. The AI visual assessment independently evaluates physical danger, disruption, and structural degradation:

| Severity Level | Priority Score Range | Default Turnaround SLA | Typical Indicators |
|---|---|---|---|
| **Critical** | **75 – 100** | **24 Hours** | Deep road craters, exposed live electrical wiring, major sewage backup into living areas, structural collapse risks. |
| **High** | **50 – 74** | **48 Hours** | Potholes on high-speed arterial roads, non-functional traffic lights, overflowing dumpsters near water sources. |
| **Medium** | **25 – 49** | **72 Hours** | Standard roadway surface deterioration, isolated streetlights out, water main seepage, uncollected dry waste. |
| **Low** | **0 – 24** | **168 Hours (7 Days)** | Minor pavement wear, faded lane markings, routine park infrastructure maintenance. |

---

## 6. Proximity-Based Duplicate Detection

Repeated reports of the same physical problem waste municipal time. SmartCivic includes an automated spatial duplicate detection module (`utils/location.py`):

### Haversine Distance Formula
When a citizen enters a report with GPS coordinates and a category, the system evaluates all active tickets (status not `RESOLVED` or `REJECTED`) within the same category using the spherical Haversine formula:

$$\Delta\sigma = 2 \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)}\right)$$

$$d = R \cdot \Delta\sigma$$

Where $R = 6,371,000\text{ meters}$.

- **Threshold:** `75.0 meters`.
- **User Alert:** If an active report exists within 75 meters, an in-form warning banner is displayed:  
  *⚠️ SIMILAR ACTIVE REPORT NEARBY (Xm away) — Submitting will link your report to increase municipal triage urgency.*
- **Master Ticket Linking:** When submitted, the duplicate ticket is linked to the primary ticket (`is_duplicate_of`), incrementing the master ticket's citizen verification count.

---

## 7. Geospatial Intelligence & GIS Map

SmartCivic embeds spatial intelligence throughout the citizen and administrative workflows:

1. **Browser Geolocation Intake**: A custom HTML5 component requests high-accuracy browser coordinates via the Streamlit bidirectional component protocol (`navigator.geolocation.getCurrentPosition`).
2. **Reverse Geocoding**: Coordinates are sent to OpenStreetMap Nominatim to automatically resolve the street address, neighborhood, city, and state.
3. **PyDeck WebGL Map Component (`components/map_view.py`)**:
   - **Scatterplot Layer**: Renders every geotagged incident as a circle marker colored by severity tier (Red for Critical, Orange for High, Amber for Medium, Green for Low) with radius dynamically scaled by priority score ($r = 18 + 0.35 \times \text{priority}$).
   - **Heatmap Layer**: An optional density heatmap weighted by incident priority score, highlighting urban problem clusters.
   - **Interactive Tooltips**: Hover tooltips displaying Complaint ID, Category, Severity, Priority, Address, and Status.
   - **Multi-Factor Filters**: Filter map points by Category, Severity, and Status simultaneously.

---

## 8. Complaint Lifecycle & SLA Governance

Every citizen report enters a transparent, verifiable operational lifecycle:

```
[ SUBMITTED ] ────► [ UNDER_REVIEW ] ────► [ ASSIGNED ] ────► [ IN_PROGRESS ] ────► [ RESOLVED ]
      │                                                                                  ▲
      └─────────────────────────────────► [ REJECTED ] ──────────────────────────────────┘
```

- **Status Transition Audit Trail**: Every status modification logs an immutable record containing the new status, timestamp, and operator dispatch note into `status_history`.
- **SLA Countdown Engine**: Dynamic SLA tracking evaluates elapsed time against target hours (`calculate_sla_status`):
  - **SLA ON TRACK**: Remaining time $> 25\%$ of target.
  - **SLA EXPIRING**: Remaining time $\le 25\%$ of target.
  - **SLA BREACHED**: Current time has exceeded deadline.
- **Before & After Resolution Proof**: When closing a ticket as `RESOLVED`, municipal operators can upload a verified repair photograph. Citizens and supervisors view the Before (citizen evidence) and After (municipal field repair) images side by side on the tracking screen.

---

## 9. Technology Stack

| Category | Technology / Library | Purpose in Current Implementation |
|---|---|---|
| **Core Language** | Python 3.10+ | Primary application runtime |
| **Frontend Framework** | Streamlit (>= 1.30.0) | Interactive single-page application framework |
| **AI / Multimodal Vision** | Google GenAI SDK (`google-genai` >= 0.1.0) | Multimodal visual classification, severity assessment, and hazard detection |
| **Data Validation** | Pydantic (>= 2.0.0) | Strict schema parsing and structured output validation |
| **Image Processing** | Pillow (PIL >= 10.0.0) | Image capture decoding, resizing, RGB conversion, and thumbnail storage |
| **Geospatial Mapping** | PyDeck (>= 0.8.0) | WebGL-powered 2D/3D scatterplot and density heatmap visualization |
| **Data Manipulation** | Pandas (>= 2.0.0) | Tabular geospatial coordinate filtering and PyDeck dataframe construction |
| **Geolocation Intake** | HTML5 Geolocation API | Browser-native GPS coordinate detection via custom component protocol |
| **Reverse Geocoding** | OpenStreetMap Nominatim API | RESTful coordinate-to-address geocoding with BigDataCloud fallback |
| **Persistence Layer** | Local JSON File Storage (`data/complaints.json`) | Atomic file persistence for complaint records and audit trails |
| **UI Styling** | Custom CSS3 Tokens | High-contrast modern civic theme with responsive media queries |
| **Version Control** | Git + GitHub | Version control and collaborative code management |
| **Deployment Target** | Streamlit Community Cloud | Cloud hosting for rapid demonstration and public access |

---

## 10. Current Prototype vs. Proposed Production Architecture

To maintain strict technical accuracy for hackathon judges and evaluators, the table below clearly separates what is **currently implemented** in this prototype from what is **proposed for future production**:

| Architectural Dimension | Current Prototype Implementation (Working Code) | Proposed Production Architecture (Future Roadmap) |
|---|---|---|
| **Frontend Client** | Responsive Python Streamlit Web Application | Native cross-platform mobile apps (Flutter / React Native) with offline camera caching |
| **Backend API Layer** | Monolithic Python execution within Streamlit runtime | Decoupled microservices architecture using FastAPI (Python) or Go/Node.js |
| **Database & Spatial Store**| Local atomic JSON (`data/complaints.json`) & local disk images | PostgreSQL with PostGIS extension for enterprise spatial indexing & polygon queries |
| **File / Object Storage** | Local filesystem storage in `data/images/` | Cloud object storage (AWS S3, Google Cloud Storage, or MinIO) with CDN delivery |
| **AI Vision Model** | Google Gemini Multimodal Vision API via `google-genai` SDK | Edge-deployed lightweight CNN/YOLO models for on-device detection + Cloud LLM orchestration |
| **GIS Infrastructure** | PyDeck WebGL component rendering in-browser points | Enterprise Tile Server (Mapbox / OpenMapTiles) with ward boundary GeoJSON geofencing |
| **Authentication & RBAC** | Session-based state without login barriers for demonstration | Role-Based Access Control (RBAC) via OAuth2 / OIDC (Citizen, Field Worker, Supervisor, Admin) |
| **Citizen Notifications** | In-app visual stepper and real-time status banners | SMS alerts (CDAC / NIC Gateway integration), WhatsApp notifications, and Push notifications |
| **Municipal ERP Sync** | Standalone queue with CSV export & Markdown dispatch sheet | Bidirectional REST/Webhook integration into municipal ERPs (e.g., CPGRAMS, SAP, e-Municipality) |

---

## 11. Project Structure

```
SIH-SmartCivic/
│
├── app.py                      # Main Streamlit application router & page renderers
├── requirements.txt            # Python dependencies (Streamlit, GenAI, PyDeck, etc.)
├── README.md                   # Comprehensive project documentation
├── .gitignore                  # Git ignore rules for secrets, virtual environments, and data
│
├── ai/                         # Multimodal Artificial Intelligence module
│   ├── __init__.py             # Exposes CIVIC_CATEGORIES and analyze_civic_issue
│   └── issue_classifier.py     # Gemini Vision inference, Pydantic schema, and fallbacks
│
├── components/                 # UI components and mapping layer
│   ├── ui_components.py        # Custom CSS design system, typography, and card tokens
│   ├── map_view.py             # PyDeck scatterplot and heatmap GIS component
│   └── geolocation_component/  # HTML5 GPS component
│       └── index.html          # Browser geolocation client script using postMessage
│
├── utils/                      # Core utility modules
│   ├── helpers.py              # ID generator, SLA calculations, and complaint schemas
│   ├── location.py             # Haversine distance, duplicate detection, and reverse geocoding
│   ├── storage.py              # Atomic JSON persistence, image handling, and analytics aggregation
│   └── export.py               # RFC 4180 CSV export and Markdown dispatch sheet generator
│
├── data/                       # Local data storage directory
│   ├── complaints.json         # Primary JSON database storing all complaint records
│   └── images/                 # Attached evidence and Before/After resolution photos
│
├── models/                     # Placeholder directory for local models
│   └── vision/                 # Reserved for future local edge/YOLO models
│
├── .streamlit/                 # Streamlit configuration
│   ├── config.toml             # Theme palette and server configuration
│   └── secrets.toml            # Private local credentials (API keys - NEVER committed)
│
└── scratch/                    # Verification test suites and diagnostic utilities
    ├── test_ai_classifier.py   # Unit test suite for Gemini Vision classification & schema
    ├── test_v04_management.py  # Unit test suite for storage, analytics, and status updates
    ├── test_v05_features.py    # Unit test suite for Haversine, duplicates, SLA, and GIS
    └── diagnose_gemini.py      # Diagnostic script verifying API keys and connectivity
```

---

## 12. Installation & Setup

### Prerequisites
- **Python 3.10** or higher installed on your system.
- A valid **Google Gemini API Key** (obtainable via [Google AI Studio](https://aistudio.google.com/)).

### Step 1: Clone the Repository
```bash
git clone https://github.com/PrintAnsh/SmartCivic.git
cd SIH-SmartCivic
```

### Step 2: Set Up a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 13. Running the Application

Launch the SmartCivic Streamlit platform:

```bash
python -m streamlit run app.py
```

Upon launch, Streamlit will provide local and network URLs:
- **Local URL:** `http://localhost:8501`
- The application will automatically open in your default web browser.

---

## 14. Google Gemini API Configuration

SmartCivic supports two secure methods for providing your Gemini API key. **Never commit your API key to Git.**

### Option A: Streamlit Secrets (Recommended for Local Dev & Streamlit Cloud)
Create or edit `.streamlit/secrets.toml` in the project root:

```toml
# .streamlit/secrets.toml
GEMINI_API_KEY = "your_actual_gemini_api_key_here"
```

> *(Note: `.streamlit/secrets.toml` is explicitly included in `.gitignore` and is never tracked by version control).*

### Option B: Environment Variable
Set the variable in your operating system terminal before running the application:

```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY="your_actual_gemini_api_key_here"

# Windows (Command Prompt)
set GEMINI_API_KEY=your_actual_gemini_api_key_here

# Linux / macOS (Bash / Zsh)
export GEMINI_API_KEY="your_actual_gemini_api_key_here"
```

---

## 15. Automated Testing & Diagnostics

SmartCivic includes a comprehensive suite of unit tests and diagnostics in the `scratch/` directory.

### Run Unit Tests
Execute the test suites to verify that storage, AI classification, duplicate detection, and SLA computations are fully operational:

```bash
# 1. Test Complaint Management, JSON Storage & Status Lifecycles (9 Tests)
python scratch/test_v04_management.py

# 2. Test Geospatial Haversine, Duplicate Clustering & SLA Logic (10 Tests)
python scratch/test_v05_features.py

# 3. Test AI Vision Classification, Schema Clamping & Fallbacks (13 Tests)
python scratch/test_ai_classifier.py
```

### Verified Test Results Summary
```
[test_v04_management.py] ── 9 passed in 0.13s  (100% OK)
[test_v05_features.py]   ── 10 passed in 0.09s (100% OK)
[test_ai_classifier.py]  ── 13 passed in 0.21s (100% OK)
-------------------------------------------------------
Total Verified Tests: 32 / 32 Passed Successfully
```

### Run Environment & API Diagnostics
Run the diagnostic script to verify model availability, API key discovery, and Nominatim reverse geocoding connectivity:

```bash
python scratch/diagnose_gemini.py
```

### Python Compilation Check
Verify syntax across all application modules:

```bash
python -m py_compile app.py components/ui_components.py components/map_view.py utils/helpers.py utils/storage.py ai/issue_classifier.py
```

---

## 16. Deployment

### Deploying to Streamlit Community Cloud
1. Push your SmartCivic repository to GitHub.
2. Log in to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click **New app**, select your repository, branch (`main`), and set the main file path to `app.py`.
4. In **Advanced settings → Secrets**, paste your Gemini API key:
   ```toml
   GEMINI_API_KEY = "your_actual_gemini_api_key_here"
   ```
5. Click **Deploy**. The application will build, install dependencies from `requirements.txt`, and provide a public HTTPS URL accessible from desktop and mobile browsers.

---

## 17. Security & Secrets Management

- **No Hardcoded Keys**: The codebase strictly accesses API keys via `get_gemini_api_key()` in `ai/issue_classifier.py`, checking Streamlit secrets and environment variables dynamically.
- **Git Ignore Enforcement**: `.gitignore` explicitly prevents tracking of:
  - `.streamlit/secrets.toml`
  - Local virtual environments (`venv/`, `.venv/`)
  - Runtime cache (`__pycache__/`, `*.pyc`)
  - Diagnostic logs (`*.log`)
- **Sanitized Exports**: CSV and Markdown dispatch sheets sanitize input fields to prevent formula injection attacks.

---

## 18. Current Prototype Limitations

In the interest of technical honesty and transparency:
- **Local JSON Storage**: Complaints are stored in `data/complaints.json`. While atomic writes prevent corruption during local use, this storage mechanism is not designed for high-concurrency concurrent writes under heavy production load.
- **Container Ephemerality**: On free hosting tiers (such as Streamlit Community Cloud), the local filesystem resets when the container restarts unless mounted to persistent network storage.
- **API Dependency**: Real-time AI classification depends on active internet connectivity and access to the Google Gemini API endpoint.
- **Browser Permissions**: GPS detection and camera input require explicit citizen permission in the browser. If denied, manual text entry and file upload serve as fallbacks.

---

## 19. Future Roadmap

Based on the Smart India Hackathon vision, the following enhancements represent the path from working prototype to scalable municipal deployment:

- [ ] **Cross-Platform Native Apps**: Develop mobile applications using Flutter / React Native with offline photographic caching for areas with poor connectivity.
- [ ] **Decoupled RESTful API**: Build a high-throughput backend using FastAPI with asynchronous worker queues (Celery / Redis).
- [ ] **PostgreSQL + PostGIS**: Migrate spatial data to PostGIS for municipal ward polygon queries, automated geofencing, and sub-second spatial indexing.
- [ ] **Hybrid Edge AI**: Deploy quantized YOLO models on edge devices for offline road defect detection, escalating edge cases to multimodal cloud LLMs.
- [ ] **Automated Municipal ERP Webhooks**: Integrate with state and national grievance redressal systems (such as CPGRAMS, Swachhata, and local municipal portals).
- [ ] **Citizen Push Notifications**: Multi-channel progress alerts via SMS gateways, WhatsApp Business API, and mobile push notifications.

---

## 20. Why SmartCivic?

| Feature / Capability | Conventional Grievance Portals | SmartCivic Platform |
|---|---|---|
| **Intake Modality** | Manual text typing and static category dropdowns | Multimodal visual photo capture + automated classification |
| **Triage Process** | Manual human review of each submission | Instant AI severity categorization and 0–100 priority scoring |
| **Duplicate Handling** | Creates redundant tickets for every report | Automated Haversine spatial clustering (<75m) merging duplicates |
| **Routing** | Manual forwarding by municipal reception desks | Instant automated routing to specialized divisions with SLA targets |
| **Verification of Work** | Simple text status change to "Closed" | Side-by-side Before/After photographic evidence comparison |
| **Spatial Oversight** | Flat tabular lists with basic text addresses | Interactive WebGL PyDeck map with density heatmaps |

---

## 21. End-to-End Use Case Walkthrough

1. **Incident Encounter**: A citizen notices a hazardous 2-meter pothole near a major intersection that poses an immediate danger to two-wheelers at night.
2. **Citizen Capture**: The citizen opens SmartCivic on their mobile browser, clicks *Detect My Location* (which auto-resolves to `"Race Course Road, Gwalior"` via GPS), and captures a live photo.
3. **AI Triage**: In seconds, Gemini Vision classifies the report as `Pothole / Road Damage`, scores urgency at `87/100 (Critical Severity)`, highlights risk factors (*"Vehicle safety hazard"*, *"Risk of night collisions"*), and recommends immediate asphalt patching.
4. **Duplicate Proximity Check**: SmartCivic checks existing active records within 75 meters. Finding none, it proceeds as a new master ticket.
5. **Municipal Dispatch**: The report is saved as `SC-2026-483921`, initiating a 24-hour Critical SLA countdown, and routes directly to the *Public Works Department (Roads & Bridges)*.
6. **Operations Dashboard**: In the municipal control room, ticket `SC-2026-483921` floats to the top of the priority-ranked triage queue. The supervisor prints the work-order dispatch brief.
7. **Resolution Verification**: The field repair crew repairs the road surface, captures an "After" photo, and updates the ticket status to `RESOLVED`.
8. **Citizen Confirmation**: The citizen enters their ticket ID on the `Track` page, observing the completed 5-step stepper and viewing the Before vs. After proof images confirming resolution.

---

## 22. Smart India Hackathon 2026 Team

**Smart Civic Issue Reporting Platform**  
*Tagline: Report. Understand. Route. Resolve.*

### Team Members
- **Purushottam K. Rajak**
- **Aditya Shrivastava**
- **Ansh Kushwah**
- **Disha Sharma**
- **Harshita Mahor**
- **Unnati Shrivastava**

---

## 23. Research & Industry References

SmartCivic draws architectural inspiration from international civic-tech best practices and Indian national e-governance standards:
- **Swachhata App (MoHUA, Government of India)**: National benchmark for citizen civic complaint monitoring and municipal sanitation feedback.
- **CPGRAMS / Centralized Public Grievance Redress and Monitoring System (DARPG)**: Guidelines for multi-tier municipal appeal workflows and administrative accountability.
- **FixMyStreet (mySociety, UK)**: Pioneers in map-centric citizen incident reporting and open civic transparency.
- **SeeClickFix (CivicPlus, USA)**: Best-in-class mobile municipal request management and automated work-order dispatching.
- **Computer Vision for Road Surface Defect Detection**: Academic research on automated pothole, crack, and pavement distress classification using deep neural networks and edge vision.
- **Digital India e-Governance Standards**: Architectural guidelines on metadata standardization, open APIs, and citizen privacy.

---

## 24. Development Status

SmartCivic is currently maintained as a **fully functional hackathon prototype** developed for the Smart India Hackathon 2026. The platform successfully demonstrates the complete automated AI-assisted civic reporting lifecycle from intake to verified closure.

---

## 25. License

License: Not specified yet.
