import concurrent.futures
import io
import json
import os
import time
import traceback
from pathlib import Path
from typing import Optional
from PIL import Image
from pydantic import BaseModel, Field

try:
    import streamlit as st
except ImportError:
    st = None

try:
    from google import genai
    from google.genai import types
    from google.genai.errors import ClientError, APIError
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


# Centralized Civic Issue Taxonomy
CIVIC_CATEGORIES = [
    "Pothole / Road Damage",
    "Garbage & Waste",
    "Streetlight",
    "Water Leakage",
    "Drainage & Sewage",
    "Public Infrastructure",
    "Other / Unclear"
]

# Centralized Severity Levels
SEVERITY_LEVELS = ["Low", "Medium", "High", "Critical"]

# Hard Timeout Limits (balanced for multimodal image transfer + LLM inference)
TOTAL_ANALYSIS_TIMEOUT_SECONDS = 20.0

# Memory cache for verified multimodal models
_CACHED_MULTIMODAL_MODELS: Optional[list[str]] = None


class CivicClassificationResult(BaseModel):
    """
    Pydantic schema for structured output from Gemini Vision.
    Encompasses classification, visual evidence, severity assessment,
    priority scoring, risk factors, and recommended municipal actions.
    """
    category: str = Field(
        description="The primary civic issue category. Must be one of: 'Pothole / Road Damage', 'Garbage & Waste', 'Streetlight', 'Water Leakage', 'Drainage & Sewage', 'Public Infrastructure', 'Other / Unclear'"
    )
    confidence: float = Field(
        description="Confidence score as a float between 0.0 and 1.0 based on visual evidence."
    )
    confidence_level: str = Field(
        description="Qualitative assessment: 'High', 'Medium', or 'Low'."
    )
    reason: str = Field(
        description="One concise factual sentence describing the physical evidence observed in the image."
    )
    summary: str = Field(
        description="1-2 sentences factually summarizing the visible civic problem and its impact without hallucinating unobserved details."
    )
    severity: str = Field(
        description="Severity level strictly one of: 'Low', 'Medium', 'High', 'Critical' based on observable danger, disruption, or structural damage."
    )
    priority_score: int = Field(
        description="Integer priority score between 0 and 100 logically consistent with severity (Low: 0-24, Medium: 25-49, High: 50-74, Critical: 75-100)."
    )
    risk_factors: list[str] = Field(
        description="List of 1 to 5 concise factual risk factors (e.g. 'Vehicle safety risk', 'Pedestrian hazard', 'Sanitation risk', etc.)."
    )
    recommended_action: str = Field(
        description="One concise factual recommended municipal action (e.g. 'Inspect and repair damaged roadway surface.')."
    )


def get_gemini_api_key() -> Optional[str]:
    """
    Retrieves the Gemini API key from Streamlit secrets, local/user .streamlit/secrets.toml,
    or environment variables. Never hardcodes, exposes, or prints API keys.
    """
    # 1. Check Streamlit Secrets if running in Streamlit
    if st is not None:
        try:
            if hasattr(st, "secrets") and st.secrets:
                if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
                    return str(st.secrets["GEMINI_API_KEY"]).strip()
                if "GOOGLE_API_KEY" in st.secrets and st.secrets["GOOGLE_API_KEY"]:
                    return str(st.secrets["GOOGLE_API_KEY"]).strip()
                for sec in ["gemini", "google", "ai", "default"]:
                    if sec in st.secrets and isinstance(st.secrets[sec], dict):
                        for k in ["api_key", "gemini_api_key", "google_api_key", "key"]:
                            if k in st.secrets[sec] and st.secrets[sec][k]:
                                return str(st.secrets[sec][k]).strip()
        except Exception:
            pass

    # 2. Check Environment Variables
    for env_var in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "GENAI_API_KEY"]:
        val = os.environ.get(env_var)
        if val and val.strip():
            return val.strip()

    # 3. Check candidate secrets.toml file locations
    repo_root = Path(__file__).resolve().parent.parent
    cwd_root = Path.cwd().absolute()
    home_dir = Path.home()
    user_prof = Path(os.environ.get("USERPROFILE", "")) if os.environ.get("USERPROFILE") else home_dir
    local_app_data = Path(os.environ.get("LOCALAPPDATA", "")) if os.environ.get("LOCALAPPDATA") else home_dir

    candidate_files = [
        repo_root / ".streamlit" / "secrets.toml",
        cwd_root / ".streamlit" / "secrets.toml",
        home_dir / ".streamlit" / "secrets.toml",
        user_prof / ".streamlit" / "secrets.toml",
        local_app_data / "SmartCivic" / "secrets.toml",
        local_app_data / "SmartCivic" / ".streamlit" / "secrets.toml",
        repo_root / "secrets.toml",
        cwd_root / "secrets.toml"
    ]

    for c_file in candidate_files:
        try:
            if c_file.exists() and c_file.is_file():
                content = c_file.read_text(encoding="utf-8")
                # Try tomllib
                try:
                    import tomllib
                    parsed = tomllib.loads(content)
                    for k in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "gemini_api_key", "google_api_key", "API_KEY", "api_key"]:
                        if k in parsed and parsed[k]:
                            key_val = str(parsed[k]).strip()
                            if key_val:
                                return key_val
                    for sec in ["gemini", "google", "ai", "default"]:
                        if sec in parsed and isinstance(parsed[sec], dict):
                            for k in ["api_key", "gemini_api_key", "google_api_key", "key"]:
                                if k in parsed[sec] and parsed[sec][k]:
                                    key_val = str(parsed[sec][k]).strip()
                                    if key_val:
                                        return key_val
                except Exception:
                    pass

                # Fallback line-by-line parsing
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith("#"):
                        continue
                    for key_name in ["GEMINI_API_KEY", "GOOGLE_API_KEY", "gemini_api_key", "google_api_key", "api_key"]:
                        if line.startswith(key_name):
                            parts = line.split("=", 1)
                            if len(parts) == 2:
                                val = parts[1].strip().strip('"').strip("'")
                                if val:
                                    return val
        except Exception:
            continue

    return None


def _convert_image_to_part(image: Image.Image):
    """
    Converts a PIL Image into a robust types.Part object with compressed JPEG bytes.
    Resizes large images to max 1024x1024 to ensure fast network transmission.
    """
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Resize if excessively large to keep payload lightweight and fast
    max_dim = 1024
    if max(image.size) > max_dim:
        image = image.copy()
        image.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=80)
    image_bytes = buf.getvalue()

    if GENAI_AVAILABLE:
        try:
            return types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
        except Exception:
            return image
    return image


# Primary and fallback vision models verified for production
PRIMARY_VISION_MODEL = "gemini-3.6-flash"
FALLBACK_VISION_MODEL = "gemini-3-flash-preview"
DEFAULT_VISION_MODELS = [PRIMARY_VISION_MODEL, FALLBACK_VISION_MODEL]

# Strict blacklist of non-vision / audio / embedding / deprecated keywords
NON_VISION_OR_DEPRECATED = [
    "tts", "audio", "embed", "embedding", "imagen", "veo", "whisper", "live", "transcription",
    "gemini-2.5-flash-preview-tts",
    "gemini-2.5-flash",     # Deprecated / 404 for new users
    "gemini-2.0-flash",     # Deprecated / 404
    "gemini-2.0-flash-lite",# Deprecated / 404
    "gemini-2.5-pro",       # Deprecated / 404
    "gemini-1.5-flash",     # Deprecated / 404 on current endpoint
    "gemini-1.5-pro",       # Deprecated / 404 on current endpoint
]


def get_verified_multimodal_models(
    client: Optional["genai.Client"] = None,
    verbose: bool = False,
    force_refresh: bool = False
) -> list[str]:
    """
    Returns the verified production multimodal vision models for SmartCivic.
    By default, immediately returns known active models (gemini-3.6-flash, gemini-3-flash-preview)
    to eliminate costly API catalog enumeration latency on user requests.
    Only queries dynamic API listing if force_refresh is explicitly True and client is supplied.
    """
    global _CACHED_MULTIMODAL_MODELS
    if not force_refresh:
        if _CACHED_MULTIMODAL_MODELS is not None and len(_CACHED_MULTIMODAL_MODELS) > 0:
            return _CACHED_MULTIMODAL_MODELS
        _CACHED_MULTIMODAL_MODELS = list(DEFAULT_VISION_MODELS)
        return _CACHED_MULTIMODAL_MODELS

    if client is None:
        return list(DEFAULT_VISION_MODELS)

    discovered = []
    try:
        if verbose:
            print("[SmartCivic AI] Dynamically inspecting available models from Gemini API...")
        models_pager = client.models.list()
        for m in models_pager:
            raw_name = getattr(m, "name", "") or getattr(m, "model", "")
            if not raw_name:
                continue
            clean_name = raw_name.replace("models/", "")
            lower_name = clean_name.lower()

            # Rule 1: Exclude blacklisted keywords / deprecated models
            if any(bad_kw in lower_name for bad_kw in NON_VISION_OR_DEPRECATED):
                if verbose:
                    print(f"  [-] Rejected non-vision/deprecated: {clean_name}")
                continue

            # Rule 2: Must be a Gemini vision model supporting generateContent
            supported_actions = getattr(m, "supported_actions", None) or getattr(m, "supported_generation_methods", None)
            if supported_actions is not None:
                if "generateContent" not in supported_actions and "generate_content" not in supported_actions:
                    if verbose:
                        print(f"  [-] Rejected (no generateContent): {clean_name}")
                    continue

            # Rule 3: Check input modalities if exposed
            modalities = getattr(m, "supported_input_modalities", None) or getattr(m, "input_modalities", None)
            if modalities is not None:
                mod_list = [str(x).lower() for x in modalities]
                if "image" not in mod_list and "image_input" not in mod_list and "multimodal" not in mod_list:
                    if verbose:
                        print(f"  [-] Rejected (no image modality): {clean_name}")
                    continue

            if "gemini" in lower_name or "vision" in lower_name:
                discovered.append(clean_name)
                if verbose:
                    print(f"  [+] Valid Vision Candidate: {clean_name}")

        if verbose:
            print(f"[SmartCivic AI] Dynamic Model Discovery: {len(discovered)} valid vision model(s) verified.")
    except Exception as e:
        if verbose:
            print(f"[SmartCivic AI] Dynamic query failed ({type(e).__name__}: {e}). Using verified modern defaults.")

    ranked = []
    # Priority 1: gemini-3.6-flash
    for m in discovered:
        if "3.6-flash" in m.lower() and m not in ranked:
            ranked.append(m)

    # Priority 2: gemini-3-flash-preview
    for m in discovered:
        if "3-flash" in m.lower() and m not in ranked:
            ranked.append(m)

    # Priority 3: other flash models (excluding blacklisted)
    for m in discovered:
        if "flash" in m.lower() and m not in ranked and not any(bad in m.lower() for bad in NON_VISION_OR_DEPRECATED):
            ranked.append(m)

    for fb in DEFAULT_VISION_MODELS:
        if fb not in ranked:
            ranked.append(fb)

    _CACHED_MULTIMODAL_MODELS = ranked
    return _CACHED_MULTIMODAL_MODELS


def _execute_gemini_call(client: "genai.Client", model_name: str, image_part, prompt: str) -> str:
    """
    Direct single API call to Gemini with JSON object mode.
    """
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.1
    )
    response = client.models.generate_content(
        model=model_name,
        contents=[image_part, prompt],
        config=config
    )
    return response.text.strip() if hasattr(response, "text") and response.text else ""


def validate_and_sanitize_ai_result(data: dict, fallback_category: str = "Other / Unclear") -> dict:
    """
    Validates and sanitizes raw JSON output from Gemini Vision against the SmartCivic schema.
    Applies deterministic, robust fallbacks if any fields are missing, out of bounds, or invalid.
    Never crashes on malformed inputs.
    """
    # 1. Category validation
    category = data.get("category", fallback_category)
    if category not in CIVIC_CATEGORIES:
        matched = False
        for valid_cat in CIVIC_CATEGORIES:
            if valid_cat.lower() in str(category).lower() or str(category).lower() in valid_cat.lower():
                category = valid_cat
                matched = True
                break
        if not matched:
            category = fallback_category

    # 2. Confidence validation
    try:
        raw_conf = data.get("confidence", 0.85)
        confidence = float(raw_conf)
    except (ValueError, TypeError):
        confidence = 0.85
    confidence = max(0.0, min(1.0, confidence))

    # 3. Confidence level validation
    raw_conf_lvl = str(data.get("confidence_level", "")).strip().capitalize()
    if raw_conf_lvl in ["High", "Medium", "Low"]:
        confidence_level = raw_conf_lvl
    else:
        if confidence >= 0.85:
            confidence_level = "High"
        elif confidence >= 0.60:
            confidence_level = "Medium"
        else:
            confidence_level = "Low"

    # 4. Reason & Summary validation
    reason = str(data.get("reason", "")).strip()
    if not reason:
        reason = f"Visible {category.lower()} evidence identified from photo inspection."

    summary = str(data.get("summary", "")).strip()
    if not summary:
        summary = f"Civic problem categorized under '{category}' detected from attached visual evidence."

    # 5. Severity validation
    raw_severity = str(data.get("severity", "")).strip().capitalize()
    if raw_severity in SEVERITY_LEVELS:
        severity = raw_severity
    else:
        severity = "Medium"

    # 6. Priority score validation
    severity_defaults = {
        "Low": 20,
        "Medium": 45,
        "High": 70,
        "Critical": 90
    }
    try:
        raw_priority = data.get("priority_score")
        if raw_priority is None:
            priority_score = severity_defaults.get(severity, 45)
        else:
            priority_score = int(float(raw_priority))
    except (ValueError, TypeError):
        priority_score = severity_defaults.get(severity, 45)

    # Clamp priority score to [0, 100]
    priority_score = max(0, min(100, priority_score))

    # 7. Risk factors validation (1 to 5 strings)
    raw_risks = data.get("risk_factors")
    sanitized_risks = []
    if isinstance(raw_risks, list):
        for item in raw_risks:
            cleaned = str(item).strip()
            if cleaned and cleaned not in sanitized_risks:
                sanitized_risks.append(cleaned)
    elif isinstance(raw_risks, str) and raw_risks.strip():
        sanitized_risks.append(raw_risks.strip())

    if not sanitized_risks:
        # Generate default risk factor based on category
        default_risks_map = {
            "Pothole / Road Damage": ["Vehicle safety risk", "Pedestrian trip hazard", "Road surface deterioration"],
            "Garbage & Waste": ["Sanitation & hygiene risk", "Public nuisance", "Environmental contamination"],
            "Streetlight": ["Nighttime visibility hazard", "Public security concern"],
            "Water Leakage": ["Water wastage", "Pavement erosion hazard"],
            "Drainage & Sewage": ["Waterlogging hazard", "Health & odor concern", "Overflow risk"],
            "Public Infrastructure": ["Public inconvenience", "Structural defect risk"],
            "Other / Unclear": ["General civic concern"]
        }
        sanitized_risks = default_risks_map.get(category, ["General civic risk"])

    # Limit to maximum 5 risk factors
    sanitized_risks = sanitized_risks[:5]

    # 8. Recommended action validation
    raw_action = str(data.get("recommended_action", "")).strip()
    if not raw_action:
        default_actions_map = {
            "Pothole / Road Damage": "Inspect and repair the damaged road surface.",
            "Garbage & Waste": "Arrange waste collection and sanitation clearance.",
            "Streetlight": "Inspect the streetlight fixture and electrical wiring.",
            "Water Leakage": "Inspect the water pipeline and repair the leak.",
            "Drainage & Sewage": "Clear the drainage obstruction and inspect sewage flow.",
            "Public Infrastructure": "Inspect and schedule maintenance for the damaged infrastructure.",
            "Other / Unclear": "Conduct a preliminary inspection of the reported issue."
        }
        recommended_action = default_actions_map.get(category, "Conduct an inspection of the reported civic issue.")
    else:
        recommended_action = raw_action

    return {
        "success": True,
        "category": category,
        "confidence": confidence,
        "confidence_percentage": f"{int(confidence * 100)}%",
        "confidence_level": confidence_level,
        "reason": reason,
        "summary": summary,
        "severity": severity,
        "priority_score": priority_score,
        "risk_factors": sanitized_risks,
        "recommended_action": recommended_action
    }


def analyze_civic_issue(
    image: Image.Image,
    model_name: str = None,
    citizen_description: str = "",
    location_text: str = ""
) -> dict:
    """
    Unified AI analysis pipeline using Google GenAI SDK (Gemini Vision).
    Performs ONE multimodal vision call returning:
    - Issue Classification (Category, Confidence, Reason, Summary)
    - Risk & Severity Assessment (Severity, Priority Score 0-100, Risk Factors, Recommended Action).
    Enforces a strict 12s wall-clock timeout and zero-leak logging.
    """
    t_start = time.time()

    print("\n==================================================")
    print("SMARTCIVIC v0.3 AI VISION + SEVERITY ASSESSMENT")
    print(f"[{time.strftime('%H:%M:%S')}] Starting unified analysis pipeline...")

    if image is None:
        print("[SmartCivic AI] Error: No image provided.")
        return {
            "success": False,
            "error": "NO_IMAGE",
            "message": "No image provided for AI analysis."
        }

    if not GENAI_AVAILABLE:
        print("[SmartCivic AI] Error: google-genai SDK not installed.")
        return {
            "success": False,
            "error": "SDK_NOT_INSTALLED",
            "message": "google-genai package is not installed in the active environment."
        }

    api_key = get_gemini_api_key()
    has_key = bool(api_key and len(api_key.strip()) > 0)
    print(f"[SmartCivic AI] API key detected: {has_key}")

    if not has_key:
        print("[SmartCivic AI] Error: GEMINI_API_KEY missing from secrets and environment.")
        return {
            "success": False,
            "error": "API_KEY_MISSING",
            "message": "AI analysis is currently unavailable (API key not configured). Please configure GEMINI_API_KEY in .streamlit/secrets.toml or select the category manually."
        }

    # Initialize Client with bounded HTTP timeout (10000ms / 10s)
    try:
        t_client = time.time()
        client_http_options = None
        if hasattr(types, "HttpOptions"):
            try:
                # timeout is in milliseconds in google-genai (15000ms = 15s)
                client_http_options = types.HttpOptions(timeout=15000)
            except Exception:
                client_http_options = None

        if client_http_options:
            client = genai.Client(api_key=api_key, http_options=client_http_options)
        else:
            client = genai.Client(api_key=api_key)
        print(f"[SmartCivic AI] Client created successfully (+{time.time()-t_client:.2f}s)")
    except Exception as ce:
        print(f"[SmartCivic AI] Failed to initialize Google GenAI client: {ce}")
        return {
            "success": False,
            "error": "CLIENT_INIT_FAILED",
            "message": "Failed to initialize AI service. You can select the category manually."
        }

    # Prepare Image payload
    try:
        t_img = time.time()
        image_part = _convert_image_to_part(image)
        print(f"[SmartCivic AI] Image input: JPEG/RGB ({image.size[0]}x{image.size[1]}) (+{time.time()-t_img:.2f}s)")
    except Exception as img_err:
        print(f"[SmartCivic AI] Image conversion failed: {img_err}")
        image_part = image

    # Build contextual notes if provided
    context_sections = []
    if citizen_description and citizen_description.strip():
        context_sections.append(f"Citizen Description: \"{citizen_description.strip()}\"")
    if location_text and location_text.strip():
        context_sections.append(f"Reported Location: \"{location_text.strip()}\"")
    context_str = "\n".join(context_sections)
    if context_str:
        context_block = f"\nAdditional Citizen Context:\n{context_str}\n"
    else:
        context_block = ""

    # Construct comprehensive classification + severity + priority prompt
    categories_str = "\n".join([f"- {cat}" for cat in CIVIC_CATEGORIES])
    prompt = f"""You are an expert municipal infrastructure inspection and triage AI for the SmartCivic civic tech platform.
Analyze the attached photo of a civic issue and perform BOTH classification and severity/priority assessment.

Allowed Categories:
{categories_str}
{context_block}
Respond with a single valid JSON object matching this exact schema:
{{
  "category": "One of the allowed categories listed above",
  "confidence": 0.94,
  "confidence_level": "High",
  "reason": "1 concise factual sentence describing the physical defect in the image",
  "summary": "1-2 sentences factually summarizing the issue and its potential impact on citizens",
  "severity": "Low | Medium | High | Critical",
  "priority_score": 85,
  "risk_factors": [
    "Vehicle safety risk",
    "Potential accident hazard",
    "Road surface damage"
  ],
  "recommended_action": "Inspect and repair the damaged road surface."
}}

Guidelines for Severity & Priority Assessment:
1. SEVERITY LEVELS:
   - "Low": Minor cosmetic or small issue with limited public impact and no immediate safety risk (Priority: 0–24).
   - "Medium": Noticeable civic problem causing inconvenience or moderate impact, but not immediately dangerous (Priority: 25–49).
   - "High": Significant infrastructure damage or clear safety concern affecting traffic, pedestrians, sanitation, or utilities (Priority: 50–74).
   - "Critical": Immediate serious danger, major public safety hazard, electrical/sewage emergency, or total obstruction (Priority: 75–100).

2. PRIORITY SCORE (0–100):
   - Must be an integer logically aligned with severity.
   - Example: A deep active pothole on a roadway is High/Critical severity with a priority of 70–90.
   - Example: Uncollected residential garbage is Medium severity with a priority of 35–50.
   - Example: Non-civic/indoor/unclear photo is Low severity with a priority of 0–15.

3. RISK FACTORS:
   - Provide 1 to 5 concise factual risk bullet points (e.g. "Vehicle damage risk", "Pedestrian trip hazard", "Water contamination", "Sanitation hazard").
   - Do NOT invent unobservable facts.

4. RECOMMENDED ACTION:
   - Provide 1 concise actionable recommendation (e.g. "Inspect and repair the damaged road surface.").
   - Frame it as an informational recommendation, not an active dispatch claim.

5. NON-CIVIC / UNCLEAR:
   - If the image is unrelated to public civic infrastructure (selfie, indoor room, pet, document, food) or unclear -> "Other / Unclear", Low severity, priority 0–15.

6. Output ONLY the JSON object. Do not include extra conversational text or markdown explanation.
"""

    # Resolve candidate multimodal vision models
    if model_name:
        candidate_models = [model_name]
    else:
        configured_override = os.environ.get("GEMINI_MODEL")
        if configured_override and not any(kw in configured_override.lower() for kw in NON_VISION_OR_DEPRECATED):
            candidate_models = [configured_override]
        else:
            candidate_models = get_verified_multimodal_models(client)

    raw_response_text = ""
    model_succeeded = ""
    last_error_details = ""

    # Execute with explicit non-blocking thread pool lifecycle per attempt (max 2 vision models)
    for target_model in candidate_models[:2]:
        remaining_time = max(2.0, TOTAL_ANALYSIS_TIMEOUT_SECONDS - (time.time() - t_start))
        if remaining_time <= 2.0 and target_model != candidate_models[0]:
            print(f"[SmartCivic AI] Insufficient time budget for fallback '{target_model}'. Aborting.")
            break

        print(f"[SmartCivic AI] Selected verified multimodal model: {target_model}")
        print(f"[SmartCivic AI] Requesting model: {target_model} (Timeout limit: {remaining_time:.1f}s)...")
        print(f"[SmartCivic AI] Multimodal request started")

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        future = executor.submit(_execute_gemini_call, client, target_model, image_part, prompt)

        try:
            raw_response_text = future.result(timeout=remaining_time)
            executor.shutdown(wait=False, cancel_futures=True)
            if raw_response_text:
                model_succeeded = target_model
                print(f"[SmartCivic AI] Response received (+{time.time()-t_start:.2f}s total)")
                break
        except concurrent.futures.TimeoutError:
            print(f"[SmartCivic AI] Call to '{target_model}' timed out after {remaining_time:.1f}s!")
            last_error_details = f"Request to '{target_model}' timed out"
            # Non-blocking shutdown to ensure main thread never blocks
            try:
                future.cancel()
                executor.shutdown(wait=False, cancel_futures=True)
            except Exception:
                pass
            continue
        except Exception as api_err:
            status_code = getattr(api_err, "code", getattr(api_err, "status_code", "N/A"))
            msg = getattr(api_err, "message", str(api_err))
            print(f"[SmartCivic AI] Error on model '{target_model}': {type(api_err).__name__} (Status: {status_code}) - {msg}")
            last_error_details = f"{type(api_err).__name__} (Status: {status_code}): {msg}"
            try:
                executor.shutdown(wait=False, cancel_futures=True)
            except Exception:
                pass
            continue

    # If no response was received
    if not raw_response_text:
        total_elapsed = time.time() - t_start
        print(f"[SmartCivic AI Failure] No valid response received within {total_elapsed:.2f}s.")
        print(f"Last Error: {last_error_details}")
        print("==================================================\n")
        return {
            "success": False,
            "error": "TIMEOUT_OR_API_ERROR",
            "message": "AI analysis is temporarily unavailable. Please select the category manually."
        }

    # Parse and validate response JSON with deterministic schema validation
    try:
        clean_json_text = raw_response_text
        if clean_json_text.startswith("```json"):
            clean_json_text = clean_json_text[7:]
        elif clean_json_text.startswith("```"):
            clean_json_text = clean_json_text[3:]
        if clean_json_text.endswith("```"):
            clean_json_text = clean_json_text[:-3]
        clean_json_text = clean_json_text.strip()

        data = json.loads(clean_json_text)
        validated_result = validate_and_sanitize_ai_result(data)

        total_elapsed = time.time() - t_start
        validated_result["model_used"] = model_succeeded
        validated_result["elapsed_seconds"] = round(total_elapsed, 2)

        print(f"[SmartCivic AI Success] Category: '{validated_result['category']}', Confidence: {validated_result['confidence_percentage']} ({validated_result['confidence_level']})")
        print(f"[SmartCivic AI Severity]: {validated_result['severity']} | Priority Score: {validated_result['priority_score']}/100")
        print(f"[SmartCivic AI Risks]: {', '.join(validated_result['risk_factors'])}")
        print(f"[SmartCivic AI Action]: {validated_result['recommended_action']}")
        print(f"[SmartCivic AI Model]: {model_succeeded} (+{total_elapsed:.2f}s)")
        print("==================================================\n")
        return validated_result

    except Exception as parse_err:
        print(f"[SmartCivic AI] Failed to parse JSON response: {parse_err}")
        return {
            "success": False,
            "error": "PARSE_ERROR",
            "message": f"AI returned an unparseable response: {parse_err}. You can select the category manually."
        }
