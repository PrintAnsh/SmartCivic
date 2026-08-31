import io
import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from PIL import Image


def get_persistent_storage_dir() -> Path:
    """
    Returns the platform-appropriate persistent application data directory outside OneDrive.
    On Windows: %LOCALAPPDATA%/SmartCivic/data (e.g. C:/Users/<User>/AppData/Local/SmartCivic/data)
    On POSIX / Fallback: ~/.smartcivic/data
    """
    if "LOCALAPPDATA" in os.environ and os.environ["LOCALAPPDATA"]:
        base = Path(os.environ["LOCALAPPDATA"]) / "SmartCivic" / "data"
    elif "APPDATA" in os.environ and os.environ["APPDATA"]:
        base = Path(os.environ["APPDATA"]) / "SmartCivic" / "data"
    else:
        base = Path.home() / ".smartcivic" / "data"

    try:
        base.mkdir(parents=True, exist_ok=True)
        (base / "images").mkdir(parents=True, exist_ok=True)
        return base
    except Exception:
        fallback = Path(tempfile.gettempdir()) / "SmartCivic" / "data"
        fallback.mkdir(parents=True, exist_ok=True)
        (fallback / "images").mkdir(parents=True, exist_ok=True)
        return fallback


DATA_DIR = get_persistent_storage_dir()
IMAGES_DIR = DATA_DIR / "images"
COMPLAINTS_FILE = DATA_DIR / "complaints.json"
STORAGE_ROOT = DATA_DIR.parent
PROJECT_ROOT = DATA_DIR.parent


def ensure_storage_dirs() -> None:
    """
    Safely ensures DATA_DIR and IMAGES_DIR exist on disk.
    """
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[SmartCivic Storage] Warning ensuring storage dirs: {e}")


def migrate_existing_data() -> None:
    """
    If repository data/complaints.json exists and local app data does not,
    safely copies existing complaints and images to the local persistent store.
    """
    repo_root = Path(__file__).parent.parent
    repo_complaints = repo_root / "data" / "complaints.json"
    repo_images = repo_root / "data" / "images"

    # Migrate complaints.json if target doesn't exist
    if repo_complaints.exists() and not COMPLAINTS_FILE.exists():
        try:
            shutil.copy2(str(repo_complaints), str(COMPLAINTS_FILE))
            print(f"[SmartCivic Storage] Migrated complaints to persistent store: {COMPLAINTS_FILE}")
        except Exception:
            pass

    # Migrate image files
    if repo_images.exists() and repo_images.is_dir():
        try:
            for img_file in repo_images.glob("*.jpg"):
                target_img = IMAGES_DIR / img_file.name
                if not target_img.exists():
                    shutil.copy2(str(img_file), str(target_img))
        except Exception:
            pass


# Ensure directories and run migration on module load
ensure_storage_dirs()
migrate_existing_data()


def resolve_image_path(img_path_str: str) -> Optional[Path]:
    """
    Resolves an image relative path to its absolute location,
    checking persistent storage root first, then repository root.
    """
    if not img_path_str:
        return None
    p = Path(img_path_str)
    if p.is_absolute() and p.exists():
        return p
    # Check under persistent PROJECT_ROOT (%LOCALAPPDATA%/SmartCivic)
    cand1 = PROJECT_ROOT / img_path_str
    if cand1.exists():
        return cand1
    # Check under REPO_ROOT
    repo_root = Path(__file__).parent.parent
    cand2 = repo_root / img_path_str
    if cand2.exists():
        return cand2
    return cand1


def load_all_complaints() -> List[Dict[str, Any]]:
    """
    Loads all persistent complaint records from complaints.json.
    If the file does not exist, seeds realistic demo data and returns it.
    """
    ensure_storage_dirs()

    if not COMPLAINTS_FILE.exists():
        return seed_demo_complaints()

    try:
        with open(str(COMPLAINTS_FILE), "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                return data
            elif isinstance(data, list) and len(data) == 0:
                return seed_demo_complaints()
            return []
    except Exception:
        return seed_demo_complaints()


def save_all_complaints(complaints: List[Dict[str, Any]]) -> bool:
    """
    Atomically saves the complete list of complaints to complaints.json.
    """
    ensure_storage_dirs()

    clean_list = []
    for c in complaints:
        rec_copy = dict(c)
        # Strip in-memory PIL Image objects from serialized JSON
        if "image" in rec_copy:
            del rec_copy["image"]
        if "resolution_image" in rec_copy:
            del rec_copy["resolution_image"]
        clean_list.append(rec_copy)

    temp_path = COMPLAINTS_FILE.with_suffix(".json.tmp")

    # Attempt 1: Atomic write with temp file
    try:
        with open(str(temp_path), "w", encoding="utf-8") as f:
            json.dump(clean_list, f, indent=2, ensure_ascii=False)
            f.flush()
        
        if temp_path.exists():
            os.replace(str(temp_path), str(COMPLAINTS_FILE))
            return True
    except Exception:
        pass

    # Attempt 2: Direct write to COMPLAINTS_FILE
    try:
        with open(str(COMPLAINTS_FILE), "w", encoding="utf-8") as f:
            json.dump(clean_list, f, indent=2, ensure_ascii=False)
            f.flush()
        return True
    except Exception as err:
        print(f"[SmartCivic Storage] Critical error saving complaints: {err}")
        return False


def save_complaint_image(complaint_id: str, image_obj: Any) -> Optional[str]:
    """
    Saves an attached PIL Image or image buffer to %LOCALAPPDATA%/SmartCivic/data/images/{complaint_id}.jpg.
    Returns project-relative path (data/images/{complaint_id}.jpg).
    """
    if image_obj is None:
        return None

    ensure_storage_dirs()

    filename = f"{complaint_id}.jpg"
    image_path = IMAGES_DIR / filename

    try:
        if isinstance(image_obj, Image.Image):
            rgb_img = image_obj.convert("RGB") if image_obj.mode != "RGB" else image_obj
            rgb_img.save(str(image_path), format="JPEG", quality=85)
            if image_path.exists():
                return f"data/images/{filename}"
        elif hasattr(image_obj, "read"):
            img = Image.open(image_obj)
            rgb_img = img.convert("RGB") if img.mode != "RGB" else img
            rgb_img.save(str(image_path), format="JPEG", quality=85)
            if hasattr(image_obj, "seek"):
                image_obj.seek(0)
            if image_path.exists():
                return f"data/images/{filename}"
    except Exception as e:
        print(f"[SmartCivic Storage] Error saving image: {e}")

    return None


def save_resolution_image(complaint_id: str, image_obj: Any) -> Optional[str]:
    """
    Saves a municipal resolution proof image (After repair photo)
    to %LOCALAPPDATA%/SmartCivic/data/images/RESOLVED-{complaint_id}.jpg.
    Returns project-relative path (data/images/RESOLVED-{complaint_id}.jpg).
    """
    if image_obj is None:
        return None

    ensure_storage_dirs()

    filename = f"RESOLVED-{complaint_id}.jpg"
    image_path = IMAGES_DIR / filename

    try:
        if isinstance(image_obj, Image.Image):
            rgb_img = image_obj.convert("RGB") if image_obj.mode != "RGB" else image_obj
            rgb_img.save(str(image_path), format="JPEG", quality=85)
            if image_path.exists():
                return f"data/images/{filename}"
        elif hasattr(image_obj, "read"):
            img = Image.open(image_obj)
            rgb_img = img.convert("RGB") if img.mode != "RGB" else img
            rgb_img.save(str(image_path), format="JPEG", quality=85)
            if hasattr(image_obj, "seek"):
                image_obj.seek(0)
            if image_path.exists():
                return f"data/images/{filename}"
    except Exception as e:
        print(f"[SmartCivic Storage] Error saving resolution image: {e}")

    return None


def save_complaint(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Saves a new complaint record or updates an existing one in persistent storage.
    Handles image saving, resolution image saving, and status audit logging.
    """
    complaints = load_all_complaints()
    complaint_id = record.get("complaint_id")

    # Save intake image to disk if present as a PIL object
    if "image" in record and record["image"] is not None and not record.get("image_path"):
        img_path = save_complaint_image(complaint_id, record["image"])
        record["image_path"] = img_path

    # Save resolution proof image if present
    if "resolution_image" in record and record["resolution_image"] is not None and not record.get("resolution_image_path"):
        res_img_path = save_resolution_image(complaint_id, record["resolution_image"])
        record["resolution_image_path"] = res_img_path

    # Ensure status history exists
    if "status_history" not in record or not record["status_history"]:
        record["status_history"] = [
            {
                "status": record.get("status", "SUBMITTED"),
                "timestamp": record.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                "note": "Citizen complaint logged via SmartCivic."
            }
        ]

    # Update or Append
    updated = False
    for i, c in enumerate(complaints):
        if c.get("complaint_id") == complaint_id:
            complaints[i] = record
            updated = True
            break

    if not updated:
        complaints.append(record)

    save_all_complaints(complaints)
    return record


def get_complaint_by_id(complaint_id: str) -> Optional[Dict[str, Any]]:
    """
    Finds a complaint record by its exact ID.
    """
    complaints = load_all_complaints()
    for c in complaints:
        if str(c.get("complaint_id", "")).strip().upper() == complaint_id.strip().upper():
            return c
    return None


def update_complaint_status(
    complaint_id: str,
    new_status: str,
    note: str = "",
    assigned_department: str = None,
    resolution_image: Any = None
) -> bool:
    """
    Updates the status, department, and resolution note for a complaint,
    optionally attaching a resolution proof photo upon marking RESOLVED.
    Logs the transition timestamp to status_history.
    """
    complaints = load_all_complaints()
    found = False
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for c in complaints:
        if c.get("complaint_id") == complaint_id:
            c["status"] = new_status
            if assigned_department:
                c["assigned_department"] = assigned_department
            if note:
                c["resolution_notes"] = note

            # If resolved, set resolution timestamp and save resolution proof image
            if new_status == "RESOLVED":
                c["resolution_timestamp"] = now_str
                if resolution_image is not None:
                    res_path = save_resolution_image(complaint_id, resolution_image)
                    if res_path:
                        c["resolution_image_path"] = res_path

            # Log to status_history
            if "status_history" not in c:
                c["status_history"] = []
            
            c["status_history"].append({
                "status": new_status,
                "timestamp": now_str,
                "note": note or f"Status updated to {new_status} by municipal triage."
            })
            found = True
            break

    if found:
        return save_all_complaints(complaints)
    return False


def link_duplicate_complaint(child_cid: str, master_cid: str) -> bool:
    """
    Links a duplicate complaint to an existing master ticket,
    incrementing the master ticket's citizen impact counter.
    """
    complaints = load_all_complaints()
    child = None
    master = None

    for c in complaints:
        if c.get("complaint_id") == child_cid:
            child = c
        elif c.get("complaint_id") == master_cid:
            master = c

    if child and master:
        child["is_duplicate_of"] = master_cid
        child["status"] = "UNDER_REVIEW"
        master["duplicate_count"] = master.get("duplicate_count", 0) + 1

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if "status_history" not in child:
            child["status_history"] = []
        child["status_history"].append({
            "status": "UNDER_REVIEW",
            "timestamp": now_str,
            "note": f"Linked as duplicate of master ticket {master_cid}."
        })

        if "status_history" not in master:
            master["status_history"] = []
        master["status_history"].append({
            "status": master.get("status", "SUBMITTED"),
            "timestamp": now_str,
            "note": f"Citizen verification added: duplicate ticket {child_cid} merged into master."
        })

        return save_all_complaints(complaints)
    return False


def compute_municipal_analytics(complaints: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes comprehensive aggregated metrics and distributions for municipal triage,
    SLA governance, and geospatial reporting.
    """
    from utils.helpers import calculate_sla_status

    total = len(complaints)
    if total == 0:
        return {
            "total_complaints": 0,
            "pending_count": 0,
            "in_progress_count": 0,
            "resolved_count": 0,
            "critical_high_count": 0,
            "avg_priority_score": 0,
            "category_distribution": {},
            "severity_distribution": {"Critical": 0, "High": 0, "Medium": 0, "Low": 0},
            "status_distribution": {},
            "department_workload": {},
            "sla_breached_count": 0,
            "sla_on_track_count": 0,
            "sla_compliance_pct": 100.0,
            "total_duplicates_merged": 0,
            "resolved_with_proof_count": 0
        }

    pending_count = sum(1 for c in complaints if c.get("status") in ["SUBMITTED", "UNDER_REVIEW"])
    in_progress_count = sum(1 for c in complaints if c.get("status") in ["ASSIGNED", "IN_PROGRESS"])
    resolved_count = sum(1 for c in complaints if c.get("status") == "RESOLVED")
    critical_high_count = sum(1 for c in complaints if c.get("severity") in ["Critical", "High"] or c.get("priority_score", 0) >= 70)

    total_priority = sum(c.get("priority_score", 50) for c in complaints)
    avg_priority = round(total_priority / total, 1)

    # SLA and Resolution Proof metrics
    sla_breached_count = 0
    sla_on_track_count = 0
    resolved_with_proof_count = 0
    total_duplicates_merged = 0

    for c in complaints:
        sla_info = calculate_sla_status(c)
        if sla_info["is_breached"]:
            sla_breached_count += 1
        else:
            sla_on_track_count += 1

        if c.get("resolution_image_path"):
            resolved_with_proof_count += 1

        if c.get("is_duplicate_of"):
            total_duplicates_merged += 1

    sla_compliance_pct = round((sla_on_track_count / total) * 100.0, 1) if total > 0 else 100.0

    # Category counts
    category_counts: Dict[str, int] = {}
    for c in complaints:
        cat = c.get("category", "Other / Unclear")
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # Severity counts
    severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for c in complaints:
        sev = c.get("severity", "Medium")
        if sev in severity_counts:
            severity_counts[sev] += 1
        else:
            severity_counts["Medium"] += 1

    # Status counts
    status_counts: Dict[str, int] = {}
    for c in complaints:
        st = c.get("status", "SUBMITTED")
        status_counts[st] = status_counts.get(st, 0) + 1

    # Department counts
    dept_counts: Dict[str, int] = {}
    for c in complaints:
        dept = c.get("assigned_department") or "Unassigned"
        dept_counts[dept] = dept_counts.get(dept, 0) + 1

    return {
        "total_complaints": total,
        "pending_count": pending_count,
        "in_progress_count": in_progress_count,
        "resolved_count": resolved_count,
        "critical_high_count": critical_high_count,
        "avg_priority_score": avg_priority,
        "category_distribution": category_counts,
        "severity_distribution": severity_counts,
        "status_distribution": status_counts,
        "department_workload": dept_counts,
        "sla_breached_count": sla_breached_count,
        "sla_on_track_count": sla_on_track_count,
        "sla_compliance_pct": sla_compliance_pct,
        "total_duplicates_merged": total_duplicates_merged,
        "resolved_with_proof_count": resolved_with_proof_count
    }


def seed_demo_complaints() -> List[Dict[str, Any]]:
    """
    Seeds realistic municipal complaint records across Gwalior civic areas
    with diverse categories, severities, priority scores, statuses, and geospatial coordinates.
    """
    ensure_storage_dirs()
    demo_records = [
        {
            "complaint_id": "SC-2026-849201",
            "timestamp": "2026-08-30 09:15:00",
            "category": "Pothole / Road Damage",
            "final_category": "Pothole / Road Damage",
            "ai_category": "Pothole / Road Damage",
            "ai_confidence": 0.96,
            "ai_confidence_level": "High",
            "ai_reason": "Severe 2-meter road crater with exposed sub-base asphalt.",
            "ai_summary": "Major cavity on high-traffic arterial road causing dangerous swerving and vehicle damage.",
            "is_ai_analyzed": True,
            "severity": "Critical",
            "priority_score": 92,
            "risk_factors": ["High vehicular collision risk", "Two-wheeler skid hazard", "Traffic bottleneck"],
            "recommended_action": "Deploy rapid asphalt patching team and place safety cones immediately.",
            "description": "Massive pothole in front of Madhav Institute gate. Multiple scooters have slipped during evening hours.",
            "location_text": "Race Course Road, Near MITS Circle, Gwalior, Madhya Pradesh, India",
            "latitude": 26.237289,
            "longitude": 78.225341,
            "image_path": None,
            "status": "IN_PROGRESS",
            "assigned_department": "Public Works Department (Roads & Bridges)",
            "resolution_notes": "Field repair squad dispatched. Cold-mix asphalt repair scheduled.",
            "resolution_image_path": None,
            "resolution_timestamp": None,
            "sla_target_hours": 24,
            "is_duplicate_of": None,
            "duplicate_count": 2,
            "status_history": [
                {"status": "SUBMITTED", "timestamp": "2026-08-30 09:15:00", "note": "Citizen complaint logged via SmartCivic."},
                {"status": "UNDER_REVIEW", "timestamp": "2026-08-30 09:30:00", "note": "AI Critical severity flagged; escalated to PWD executive engineer."},
                {"status": "ASSIGNED", "timestamp": "2026-08-30 10:00:00", "note": "Assigned to PWD Road Maintenance Squad #3."},
                {"status": "IN_PROGRESS", "timestamp": "2026-08-30 11:45:00", "note": "Work crew on site; road cones placed."}
            ]
        },
        {
            "complaint_id": "SC-2026-512048",
            "timestamp": "2026-08-30 10:22:00",
            "category": "Garbage & Waste",
            "final_category": "Garbage & Waste",
            "ai_category": "Garbage & Waste",
            "ai_confidence": 0.94,
            "ai_confidence_level": "High",
            "ai_reason": "Overflowing municipal dumpster spilling onto pedestrian walkway.",
            "ai_summary": "Uncollected organic and plastic waste creating health hazards and odor nuisance.",
            "is_ai_analyzed": True,
            "severity": "High",
            "priority_score": 78,
            "risk_factors": ["Public health hazard", "Stray animal gathering", "Pedestrian obstruction"],
            "recommended_action": "Dispatch compactor truck for waste clearance and sanitize collection point.",
            "description": "Dumpster overflowing for 3 consecutive days. Foul odor spreading into nearby market shops.",
            "location_text": "Sarafa Bazaar, Lashkar, Gwalior, Madhya Pradesh, India",
            "latitude": 26.208154,
            "longitude": 78.163422,
            "image_path": None,
            "status": "ASSIGNED",
            "assigned_department": "Sanitation & Solid Waste Management",
            "resolution_notes": "Assigned to Ward 14 Sanitation Inspector.",
            "resolution_image_path": None,
            "resolution_timestamp": None,
            "sla_target_hours": 48,
            "is_duplicate_of": None,
            "duplicate_count": 0,
            "status_history": [
                {"status": "SUBMITTED", "timestamp": "2026-08-30 10:22:00", "note": "Citizen complaint logged via SmartCivic."},
                {"status": "UNDER_REVIEW", "timestamp": "2026-08-30 10:45:00", "note": "Reviewed by Central Sanitation Control Room."},
                {"status": "ASSIGNED", "timestamp": "2026-08-30 11:15:00", "note": "Assigned to Ward 14 Compactor Truck Route."}
            ]
        },
        {
            "complaint_id": "SC-2026-319842",
            "timestamp": "2026-08-30 11:05:00",
            "category": "Streetlight",
            "final_category": "Streetlight",
            "ai_category": "Streetlight",
            "ai_confidence": 0.91,
            "ai_confidence_level": "High",
            "ai_reason": "Leaning streetlight pole with non-functional LED luminaire.",
            "ai_summary": "Dark roadway stretch creating security concerns and nocturnal navigation hazards.",
            "is_ai_analyzed": True,
            "severity": "Medium",
            "priority_score": 48,
            "risk_factors": ["Nighttime pedestrian hazard", "Reduced vehicle visibility"],
            "recommended_action": "Inspect electrical feeder line and replace luminaire unit.",
            "description": "Four streetlights in a row not turning on at night. Road is completely pitch black.",
            "location_text": "Maharaj Bada Link Road, Gwalior, Madhya Pradesh, India",
            "latitude": 26.215430,
            "longitude": 78.172550,
            "image_path": None,
            "status": "SUBMITTED",
            "assigned_department": "Electrical & Streetlighting Division",
            "resolution_notes": "",
            "resolution_image_path": None,
            "resolution_timestamp": None,
            "sla_target_hours": 72,
            "is_duplicate_of": None,
            "duplicate_count": 0,
            "status_history": [
                {"status": "SUBMITTED", "timestamp": "2026-08-30 11:05:00", "note": "Citizen complaint logged via SmartCivic."}
            ]
        },
        {
            "complaint_id": "SC-2026-724190",
            "timestamp": "2026-08-30 12:40:00",
            "category": "Water Leakage",
            "final_category": "Water Leakage",
            "ai_category": "Water Leakage",
            "ai_confidence": 0.95,
            "ai_confidence_level": "High",
            "ai_reason": "Pressurized clean water fountain spurting from underground distribution pipe.",
            "ai_summary": "Underground pipe burst resulting in substantial water loss and road surface erosion.",
            "is_ai_analyzed": True,
            "severity": "Critical",
            "priority_score": 89,
            "risk_factors": ["Potable water wastage", "Sub-surface road washaway", "Low water pressure in locality"],
            "recommended_action": "Isolate pipeline segment and dispatch emergency plumbing team.",
            "description": "Main water supply pipeline burst. Thousands of liters of clean drinking water flooding the street.",
            "location_text": "City Center, Near High Court Bench, Gwalior, Madhya Pradesh, India",
            "latitude": 26.202410,
            "longitude": 78.194230,
            "image_path": None,
            "status": "IN_PROGRESS",
            "assigned_department": "Water Supply & Hydro Board",
            "resolution_notes": "Emergency isolation valve closed. Pipeline excavation in progress.",
            "resolution_image_path": None,
            "resolution_timestamp": None,
            "sla_target_hours": 24,
            "is_duplicate_of": None,
            "duplicate_count": 1,
            "status_history": [
                {"status": "SUBMITTED", "timestamp": "2026-08-30 12:40:00", "note": "Citizen complaint logged via SmartCivic."},
                {"status": "UNDER_REVIEW", "timestamp": "2026-08-30 12:50:00", "note": "Emergency water loss flagged."},
                {"status": "IN_PROGRESS", "timestamp": "2026-08-30 13:10:00", "note": "Water board emergency team on site."}
            ]
        },
        {
            "complaint_id": "SC-2026-904321",
            "timestamp": "2026-08-30 13:15:00",
            "category": "Drainage & Sewage",
            "final_category": "Drainage & Sewage",
            "ai_category": "Drainage & Sewage",
            "ai_confidence": 0.93,
            "ai_confidence_level": "High",
            "ai_reason": "Overflowing manhole with dark stagnant effluent pooling across roadway.",
            "ai_summary": "Blocked sewer main leading to contamination, vehicle obstruction, and biological hazard.",
            "is_ai_analyzed": True,
            "severity": "High",
            "priority_score": 82,
            "risk_factors": ["Contamination risk", "Severe foul odor", "Disease vector breeding"],
            "recommended_action": "Deploy jetting machine to clear sewer line obstruction.",
            "description": "Sewage overflowing from manhole chamber. Stagnant contaminated water spreading into residential driveways.",
            "location_text": "Thatipur Main Market, Gwalior, Madhya Pradesh, India",
            "latitude": 26.223890,
            "longitude": 78.209120,
            "image_path": None,
            "status": "UNDER_REVIEW",
            "assigned_department": "Drainage & Sewage Operations",
            "resolution_notes": "",
            "resolution_image_path": None,
            "resolution_timestamp": None,
            "sla_target_hours": 48,
            "is_duplicate_of": None,
            "duplicate_count": 0,
            "status_history": [
                {"status": "SUBMITTED", "timestamp": "2026-08-30 13:15:00", "note": "Citizen complaint logged via SmartCivic."},
                {"status": "UNDER_REVIEW", "timestamp": "2026-08-30 13:30:00", "note": "Assigned for jetting vehicle dispatch."}
            ]
        },
        {
            "complaint_id": "SC-2026-118943",
            "timestamp": "2026-08-29 16:30:00",
            "category": "Public Infrastructure",
            "final_category": "Public Infrastructure",
            "ai_category": "Public Infrastructure",
            "ai_confidence": 0.89,
            "ai_confidence_level": "High",
            "ai_reason": "Broken concrete footpath slabs with exposed steel rebar.",
            "ai_summary": "Displaced pedestrian pavers presenting trip hazards for walkers and elderly citizens.",
            "is_ai_analyzed": True,
            "severity": "Medium",
            "priority_score": 45,
            "risk_factors": ["Pedestrian trip hazard", "Obstacle for visually impaired"],
            "recommended_action": "Realign and replace broken footpath pavers.",
            "description": "Footpath pavers damaged during underground cable laying. Left unrepaired for 2 weeks.",
            "location_text": "Phoolbagh Garden Perimeter, Gwalior, Madhya Pradesh, India",
            "latitude": 26.218550,
            "longitude": 78.174820,
            "image_path": None,
            "status": "RESOLVED",
            "assigned_department": "Public Parks & Civic Infrastructure",
            "resolution_notes": "Paver blocks re-leveled and mortared. Site inspection verified by junior engineer.",
            "resolution_image_path": None,
            "resolution_timestamp": "2026-08-30 14:00:00",
            "sla_target_hours": 72,
            "is_duplicate_of": None,
            "duplicate_count": 0,
            "status_history": [
                {"status": "SUBMITTED", "timestamp": "2026-08-29 16:30:00", "note": "Citizen complaint logged via SmartCivic."},
                {"status": "ASSIGNED", "timestamp": "2026-08-30 08:30:00", "note": "Assigned to zonal civil maintenance contractor."},
                {"status": "IN_PROGRESS", "timestamp": "2026-08-30 10:00:00", "note": "Replacement paver blocks delivered and installed."},
                {"status": "RESOLVED", "timestamp": "2026-08-30 14:00:00", "note": "Repairs completed and verified."}
            ]
        }
    ]

    save_all_complaints(demo_records)
    return demo_records
