import io
import math
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ExifTags


def extract_exif_gps(image_obj: Any) -> Tuple[Optional[float], Optional[float]]:
    """
    Extracts geographic coordinates (latitude, longitude) from an image's EXIF metadata.
    Accepts a PIL Image, file path, or file-like buffer (e.g. UploadedFile).
    Returns (latitude, longitude) in decimal degrees, or (None, None) if unavailable.
    """
    if image_obj is None:
        return None, None

    pil_img = None
    should_close = False

    try:
        if isinstance(image_obj, Image.Image):
            pil_img = image_obj
        elif isinstance(image_obj, (str, Path)):
            pil_img = Image.open(str(image_obj))
            should_close = True
        elif hasattr(image_obj, "read"):
            pos = image_obj.tell() if hasattr(image_obj, "tell") else None
            pil_img = Image.open(image_obj)
            should_close = True
            if hasattr(image_obj, "seek") and pos is not None:
                image_obj.seek(pos)
        else:
            return None, None

        exif = pil_img.getexif()
        if not exif:
            return None, None

        gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)
        if not gps_ifd:
            return None, None

        lat_raw = gps_ifd.get(ExifTags.GPS.GPSLatitude)
        lat_ref = gps_ifd.get(ExifTags.GPS.GPSLatitudeRef, "N")
        lon_raw = gps_ifd.get(ExifTags.GPS.GPSLongitude)
        lon_ref = gps_ifd.get(ExifTags.GPS.GPSLongitudeRef, "E")

        if not lat_raw or not lon_raw:
            return None, None

        def convert_coord_to_decimal(coord_val) -> Optional[float]:
            try:
                # Format: (degrees, minutes, seconds)
                if isinstance(coord_val, (list, tuple)) and len(coord_val) == 3:
                    d = float(coord_val[0])
                    m = float(coord_val[1])
                    s = float(coord_val[2])
                    return d + (m / 60.0) + (s / 3600.0)
                elif isinstance(coord_val, (int, float)):
                    return float(coord_val)
            except Exception:
                return None
            return None

        lat_dec = convert_coord_to_decimal(lat_raw)
        lon_dec = convert_coord_to_decimal(lon_raw)

        if lat_dec is None or lon_dec is None:
            return None, None

        if str(lat_ref).strip().upper() == "S":
            lat_dec = -abs(lat_dec)
        if str(lon_ref).strip().upper() == "W":
            lon_dec = -abs(lon_dec)

        # Validate coordinate limits
        if -90.0 <= lat_dec <= 90.0 and -180.0 <= lon_dec <= 180.0:
            return round(lat_dec, 6), round(lon_dec, 6)

        return None, None

    except Exception as e:
        print(f"[SmartCivic Geotag] EXIF GPS extraction error: {e}")
        return None, None
    finally:
        if should_close and pil_img:
            try:
                pil_img.close()
            except Exception:
                pass


def embed_exif_gps(
    img: Image.Image,
    lat: float,
    lon: float,
    timestamp: Optional[str] = None
) -> Image.Exif:
    """
    Constructs an Exif metadata structure containing standard GPS IFD tags
    for saving into a JPEG image.
    """
    exif = img.getexif()
    gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)

    if lat is not None and lon is not None:
        lat_abs = abs(lat)
        lat_deg = int(lat_abs)
        lat_min = int((lat_abs - lat_deg) * 60)
        lat_sec = round(((lat_abs - lat_deg) * 60 - lat_min) * 60, 4)

        lon_abs = abs(lon)
        lon_deg = int(lon_abs)
        lon_min = int((lon_abs - lon_deg) * 60)
        lon_sec = round(((lon_abs - lon_deg) * 60 - lon_min) * 60, 4)

        gps_ifd[ExifTags.GPS.GPSLatitudeRef] = "N" if lat >= 0 else "S"
        gps_ifd[ExifTags.GPS.GPSLatitude] = (lat_deg, lat_min, lat_sec)
        gps_ifd[ExifTags.GPS.GPSLongitudeRef] = "E" if lon >= 0 else "W"
        gps_ifd[ExifTags.GPS.GPSLongitude] = (lon_deg, lon_min, lon_sec)

    if timestamp:
        try:
            dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            gps_ifd[ExifTags.GPS.GPSDateStamp] = dt.strftime("%Y:%m:%d")
            gps_ifd[ExifTags.GPS.GPSTimeStamp] = (dt.hour, dt.minute, dt.second)
        except Exception:
            pass

    exif[ExifTags.Base.GPSInfo] = gps_ifd
    return exif


def add_geotag_watermark(
    img: Image.Image,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    location_text: Optional[str] = None,
    timestamp: Optional[str] = None,
    complaint_id: Optional[str] = None,
    category: Optional[str] = None,
    tag_type: str = "CITIZEN EVIDENCE"
) -> Image.Image:
    """
    Renders an official civic geotag banner overlay at the bottom of the image.
    Includes GPS coordinates, reverse-geocoded location, timestamp, and verification ID.
    """
    # Create working copy in RGBA for clean alpha overlay
    base_img = img.convert("RGBA") if img.mode != "RGBA" else img.copy()
    w, h = base_img.size

    # Responsive banner height (between 18% and 24% of height, min 85px, max 240px)
    banner_height = max(85, min(int(h * 0.22), 240))
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Semi-transparent dark background (matching SmartCivic theme #06101E with 90% opacity)
    banner_y0 = h - banner_height
    draw.rectangle([(0, banner_y0), (w, h)], fill=(6, 16, 30, 230))

    # Top accent line (Red-coral for Citizen Evidence, Emerald-green for Municipal Resolution)
    is_resolution = "RESOLUTION" in tag_type.upper() or "RESOLVED" in tag_type.upper()
    accent_color = (16, 185, 129, 255) if is_resolution else (196, 93, 99, 255)
    line_thickness = max(3, int(h * 0.005))
    draw.rectangle([(0, banner_y0), (w, banner_y0 + line_thickness)], fill=accent_color)

    # Dynamic font scaling
    font_size_main = max(12, int(banner_height * 0.16))
    font_size_sub = max(10, int(banner_height * 0.125))

    font_main = None
    font_bold = None
    font_sub = None

    for font_family in ["arialbd.ttf", "segoeuib.ttf", "Roboto-Bold.ttf"]:
        try:
            font_bold = ImageFont.truetype(font_family, font_size_main)
            break
        except Exception:
            pass

    for font_family in ["arial.ttf", "segoeui.ttf", "Roboto-Regular.ttf"]:
        try:
            font_main = ImageFont.truetype(font_family, font_size_main)
            font_sub = ImageFont.truetype(font_family, font_size_sub)
            break
        except Exception:
            pass

    if font_main is None:
        font_main = ImageFont.load_default()
        font_bold = font_main
        font_sub = font_main

    margin_x = max(14, int(w * 0.03))
    line_y = banner_y0 + max(8, int(banner_height * 0.1))
    line_spacing = max(16, int(banner_height * 0.21))

    # Line 1: Header / Badge + Ticket ID
    badge_title = f"SMARTCIVIC · {tag_type.upper()}"
    draw.text((margin_x, line_y), badge_title, font=font_bold, fill=(255, 255, 255, 255))

    if complaint_id:
        cid_text = f"ID: {complaint_id}"
        # Measure text width roughly if getbbox not supported or for clean alignment
        try:
            bbox = font_bold.getbbox(cid_text)
            text_w = bbox[2] - bbox[0]
        except Exception:
            text_w = int(len(cid_text) * font_size_main * 0.65)
        pos_x = max(margin_x + 10, w - margin_x - text_w)
        draw.text((pos_x, line_y), cid_text, font=font_bold, fill=accent_color)

    line_y += line_spacing

    # Line 2: GPS Coordinates + Timestamp
    coord_part = f"GPS: {lat:.6f}, {lon:.6f}" if (lat is not None and lon is not None) else "GPS: Coordinates Unavailable"
    time_part = f"TIME: {timestamp}" if timestamp else ""
    line2 = f"{coord_part}   |   {time_part}".strip(" | ")
    draw.text((margin_x, line_y), line2, font=font_sub, fill=(225, 230, 240, 255))

    line_y += line_spacing

    # Line 3: Location Address (safely truncated to fit width)
    if location_text:
        char_limit = max(30, int((w - margin_x * 2) / (font_size_sub * 0.58)))
        clean_loc = location_text.replace("\n", " ").strip()
        disp_loc = (clean_loc[:char_limit - 3] + "...") if len(clean_loc) > char_limit else clean_loc
        draw.text((margin_x, line_y), f"LOC: {disp_loc}", font=font_sub, fill=(185, 195, 210, 255))
        line_y += line_spacing

    # Line 4: Category
    if category:
        draw.text((margin_x, line_y), f"CAT: {category}", font=font_sub, fill=(160, 175, 195, 255))

    combined = Image.alpha_composite(base_img, overlay)
    return combined.convert("RGB")


def geotag_and_save_image(
    image_obj: Any,
    output_path: Path,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    location_text: Optional[str] = None,
    timestamp: Optional[str] = None,
    complaint_id: Optional[str] = None,
    category: Optional[str] = None,
    tag_type: str = "CITIZEN EVIDENCE"
) -> bool:
    """
    Applies visual geotag watermark stamp and embeds standard EXIF GPS tags,
    then saves the resulting JPEG image to output_path.
    """
    try:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Open image
        if isinstance(image_obj, Image.Image):
            base_img = image_obj.copy()
        elif hasattr(image_obj, "read"):
            pos = image_obj.tell() if hasattr(image_obj, "tell") else None
            base_img = Image.open(image_obj)
            if hasattr(image_obj, "seek") and pos is not None:
                image_obj.seek(pos)
        else:
            return False

        # If image already has EXIF GPS and no lat/lon was passed, extract it
        if latitude is None or longitude is None:
            ex_lat, ex_lon = extract_exif_gps(base_img)
            if ex_lat is not None and ex_lon is not None:
                latitude = ex_lat
                longitude = ex_lon

        # Watermark the image
        watermarked_img = add_geotag_watermark(
            img=base_img,
            lat=latitude,
            lon=longitude,
            location_text=location_text,
            timestamp=timestamp,
            complaint_id=complaint_id,
            category=category,
            tag_type=tag_type
        )

        # Prepare EXIF GPS
        exif = None
        if latitude is not None and longitude is not None:
            try:
                exif = embed_exif_gps(watermarked_img, latitude, longitude, timestamp)
            except Exception as e:
                print(f"[SmartCivic Geotag] Error preparing EXIF tags: {e}")

        # Save to disk
        if exif:
            watermarked_img.save(str(output_path), format="JPEG", quality=88, exif=exif)
        else:
            watermarked_img.save(str(output_path), format="JPEG", quality=88)

        return output_path.exists()

    except Exception as e:
        print(f"[SmartCivic Geotag] Error geotagging and saving image: {e}")
        return False
