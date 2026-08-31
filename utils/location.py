import json
import math
import urllib.error
import urllib.parse
import urllib.request
import streamlit.components.v1 as components


def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates great-circle distance between two geographic coordinates on Earth in meters.
    Uses spherical Haversine formula (Earth radius ~ 6,371,000 meters).
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return float("inf")

    # Convert decimal degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    distance_meters = 6371000.0 * c
    return round(distance_meters, 2)


def find_nearby_potential_duplicates(
    category: str,
    lat: float,
    lon: float,
    complaints: list,
    radius_meters: float = 75.0
) -> list:
    """
    Identifies active complaint records matching the same civic category within radius_meters.
    Returns sorted list of matches with distance_meters appended.
    """
    if lat is None or lon is None or not category:
        return []

    matches = []
    for c in complaints:
        # Ignore closed or rejected tickets
        if c.get("status") in ["RESOLVED", "REJECTED"]:
            continue

        c_cat = c.get("category", "")
        # Match identical category or related category
        if c_cat == category or c.get("final_category") == category:
            c_lat = c.get("latitude")
            c_lon = c.get("longitude")
            if c_lat is not None and c_lon is not None:
                dist = calculate_haversine_distance(lat, lon, c_lat, c_lon)
                if dist <= radius_meters:
                    match_rec = dict(c)
                    match_rec["distance_meters"] = dist
                    matches.append(match_rec)

    # Sort by closest first
    matches.sort(key=lambda x: x["distance_meters"])
    return matches



def reverse_geocode(latitude: float, longitude: float) -> str:
    """
    Performs multi-provider reverse geocoding for a given latitude and longitude.
    1. Primary: OpenStreetMap Nominatim
    2. Fallback: BigDataCloud Reverse Geocoding API
    3. Fallback: Photon / Komoot OpenStreetMap Reverse Geocoder
    Converts coordinates into a clean, concise, human-readable address (e.g. 'Gwalior, Madhya Pradesh, India').
    """
    if latitude is None or longitude is None:
        print("[SmartCivic Geocode] Latitude or longitude is None. Skipping request.")
        return ""

    print(f"=== REVERSE GEOCODE REQUEST ===")
    print(f"Input coordinates: ({latitude}, {longitude})")

    # Provider 1: OpenStreetMap Nominatim
    try:
        url_nom = f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={latitude}&lon={longitude}&zoom=18&addressdetails=1"
        headers = {
            "User-Agent": "SmartCivic-CivicPlatform/1.0 (Smart India Hackathon Project; contact: support@smartcivic.org)",
            "Accept-Language": "en"
        }
        print(f"[Nominatim URL]: {url_nom}")
        req = urllib.request.Request(url_nom, headers=headers)
        with urllib.request.urlopen(req, timeout=4.0) as response:
            status_code = response.status
            print(f"[Nominatim Status]: {status_code}")
            if status_code == 200:
                data = json.loads(response.read().decode("utf-8"))
                address = data.get("address", {})

                parts = []
                # Road / Street
                road = address.get("road") or address.get("pedestrian") or address.get("street") or address.get("footway")
                if road:
                    parts.append(road)

                # Suburb / Neighborhood / Locality
                suburb = address.get("suburb") or address.get("neighbourhood") or address.get("residential") or address.get("subdistrict")
                if suburb and suburb not in parts:
                    parts.append(suburb)

                # City / Town / District
                city = address.get("city") or address.get("town") or address.get("city_district") or address.get("district") or address.get("county")
                if city and city not in parts:
                    parts.append(city)

                # State
                state = address.get("state")
                if state and state not in parts:
                    parts.append(state)

                # Country
                country = address.get("country")
                if country and country not in parts:
                    parts.append(country)

                if parts:
                    addr_str = ", ".join(parts)
                    print(f"[Nominatim Result]: {addr_str}")
                    return addr_str

                display_name = data.get("display_name")
                if display_name:
                    segments = [s.strip() for s in display_name.split(",") if s.strip()]
                    addr_str = ", ".join(segments[:4])
                    print(f"[Nominatim Display Result]: {addr_str}")
                    return addr_str
    except Exception as e:
        print(f"[Nominatim Error]: {type(e).__name__} - {e}")

    # Provider 2: BigDataCloud Reverse Geocoding API (Fast & Reliable Fallback)
    try:
        url_bdc = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={latitude}&longitude={longitude}&localityLanguage=en"
        print(f"[BigDataCloud URL]: {url_bdc}")
        req_bdc = urllib.request.Request(url_bdc, headers={"User-Agent": "SmartCivic-CivicPlatform/1.0"})
        with urllib.request.urlopen(req_bdc, timeout=4.0) as response:
            status_code = response.status
            print(f"[BigDataCloud Status]: {status_code}")
            if status_code == 200:
                data = json.loads(response.read().decode("utf-8"))
                parts = []
                locality = data.get("locality") or data.get("localityInfo", {}).get("informative", [{}])[0].get("name")
                city = data.get("city")
                principal_sub = data.get("principalSubdivision")  # State
                country = data.get("countryName")

                if locality:
                    parts.append(locality)
                if city and city not in parts:
                    parts.append(city)
                if principal_sub and principal_sub not in parts:
                    parts.append(principal_sub)
                if country and country not in parts:
                    parts.append(country)

                if parts:
                    addr_str = ", ".join(parts)
                    print(f"[BigDataCloud Result]: {addr_str}")
                    return addr_str
    except Exception as e:
        print(f"[BigDataCloud Error]: {type(e).__name__} - {e}")

    # Provider 3: Photon / Komoot OpenStreetMap Geocoder Fallback
    try:
        url_photon = f"https://photon.komoot.io/reverse?lat={latitude}&lon={longitude}"
        print(f"[Photon URL]: {url_photon}")
        req_photon = urllib.request.Request(url_photon, headers={"User-Agent": "SmartCivic-CivicPlatform/1.0"})
        with urllib.request.urlopen(req_photon, timeout=4.0) as response:
            status_code = response.status
            print(f"[Photon Status]: {status_code}")
            if status_code == 200:
                data = json.loads(response.read().decode("utf-8"))
                features = data.get("features", [])
                if features:
                    props = features[0].get("properties", {})
                    parts = []
                    for key in ["name", "street", "district", "city", "state", "country"]:
                        val = props.get(key)
                        if val and val not in parts:
                            parts.append(val)
                    if parts:
                        addr_str = ", ".join(parts)
                        print(f"[Photon Result]: {addr_str}")
                        return addr_str
    except Exception as e:
        print(f"[Photon Error]: {type(e).__name__} - {e}")

    return ""


def render_geolocation_component(current_lat=None, current_lon=None):
    """
    Renders an HTML5 browser Geolocation button matching the SmartCivic dark editorial theme.
    Prompts browser permission only on user gesture and safely synchronizes coordinates via history.replaceState.
    """
    btn_text = "<span>📍</span> Detect My Location"
    status_init = ""
    status_style = "display: none;"
    if current_lat is not None and current_lon is not None:
        btn_text = f"<span>📍</span> Detected ({current_lat:.6f}, {current_lon:.6f})"
        status_init = f"Location detected: {current_lat:.6f}, {current_lon:.6f}"
        status_style = "color: #10B981;"

    html_code = f"""
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        .geo-btn {{
            background-color: transparent;
            color: #EBEBEB;
            border: 1px solid #3A3A3A;
            padding: 10px 18px;
            font-size: 0.88rem;
            font-weight: 600;
            letter-spacing: 0.03em;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s ease;
            width: 100%;
            justify-content: center;
            box-sizing: border-box;
        }}
        .geo-btn:hover {{
            border-color: #B15258;
            color: #FFFFFF;
            background-color: rgba(177, 82, 88, 0.12);
        }}
        .geo-btn:active {{
            transform: scale(0.99);
        }}
        .geo-status {{
            font-size: 0.78rem;
            color: #888888;
            margin-top: 6px;
            text-align: center;
            min-height: 18px;
        }}
    </style>

    <button type="button" class="geo-btn" id="detectBtn" onclick="detectGPS()">
        {btn_text}
    </button>
    <div id="statusMsg" class="geo-status" style="{status_style}">{status_init}</div>

    <script>
    function detectGPS() {{
        const btn = document.getElementById('detectBtn');
        const status = document.getElementById('statusMsg');

        if (!navigator.geolocation) {{
            status.style.display = "block";
            status.innerText = "Geolocation is not supported by your browser. Please enter location manually.";
            status.style.color = "#C45D63";
            return;
        }}

        btn.disabled = true;
        btn.innerText = "Requesting GPS coordinates...";
        status.style.display = "block";
        status.innerText = "Waiting for browser permission...";
        status.style.color = "#888888";

        navigator.geolocation.getCurrentPosition(
            function(position) {{
                const lat = position.coords.latitude.toFixed(6);
                const lon = position.coords.longitude.toFixed(6);

                btn.disabled = false;
                btn.innerHTML = "<span>📍</span> Detected (" + lat + ", " + lon + ")";
                status.innerText = "Location detected: " + lat + ", " + lon;
                status.style.color = "#10B981";

                // Update URL search parameters without navigating or reloading the top window
                try {{
                    const parentUrl = new URL(window.parent.location.href);
                    parentUrl.searchParams.set("geo_lat", lat);
                    parentUrl.searchParams.set("geo_lon", lon);
                    window.parent.history.replaceState({{}}, "", parentUrl.toString());
                }} catch (e) {{
                    console.log("URL param update:", e);
                }}

                try {{
                    window.parent.sessionStorage.setItem("smartcivic_geo_lat", lat);
                    window.parent.sessionStorage.setItem("smartcivic_geo_lon", lon);
                }} catch (e) {{}}
            }},
            function(error) {{
                btn.disabled = false;
                btn.innerHTML = "<span>📍</span> Detect My Location";
                let errText = "Unable to detect your location. Please enter location manually.";
                if (error.code === error.PERMISSION_DENIED) {{
                    errText = "Location permission denied. Please enter location manually.";
                }} else if (error.code === error.POSITION_UNAVAILABLE) {{
                    errText = "Location unavailable. Please enter location manually.";
                }} else if (error.code === error.TIMEOUT) {{
                    errText = "Location request timed out. Please enter location manually.";
                }}
                status.innerText = errText;
                status.style.color = "#C45D63";
            }},
            {{
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }}
        );
    }}
    </script>
    """
    components.html(html_code, height=65)
