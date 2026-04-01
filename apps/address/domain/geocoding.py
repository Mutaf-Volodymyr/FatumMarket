import re

from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim

from config import settings

geolocator = Nominatim(user_agent=settings.NOMINATIM_USER_AGENT)

MOLDOVA_BOUNDS = {
    "lat_min": 45.4,
    "lat_max": 48.5,
    "lon_min": 26.6,
    "lon_max": 30.2,
}


APARTMENT_REGEX = re.compile(
    r"(кв\.?|apt\.?|ap\.?|apartment|apartament|apart\.?)\s*\d+",
    re.IGNORECASE,
)


def normalize_address_for_geocoding(raw: str) -> str:
    cleaned = APARTMENT_REGEX.sub("", raw)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    return cleaned.strip()


def geocode_address(address: str):
    address = normalize_address_for_geocoding(address)
    try:
        location = geolocator.geocode(
            address,
            addressdetails=True,
            language="ro",
            country_codes="md",
            timeout=10,
        )
    except GeocoderTimedOut:
        return None, "timeout"

    if not location:
        return None, "not_found"

    lat, lon = location.latitude, location.longitude

    if not (
        MOLDOVA_BOUNDS["lat_min"] <= lat <= MOLDOVA_BOUNDS["lat_max"]
        and MOLDOVA_BOUNDS["lon_min"] <= lon <= MOLDOVA_BOUNDS["lon_max"]
    ):
        return None, "outside_moldova"

    return {
        "lat": lat,
        "lon": lon,
        "address": location.raw.get("address", {}),
    }, None
