"""GeoJSON helper utilities."""
import json
import math


def make_polygon(lat: float, lon: float, area_ha: float) -> str:
    """Generate a simple rectangular GeoJSON polygon around a centroid.

    Args:
        lat: Centroid latitude.
        lon: Centroid longitude.
        area_ha: Desired area in hectares.

    Returns:
        GeoJSON Polygon string.
    """
    km_per_deg_lat = 111.0
    km_per_deg_lon = 111.0 * math.cos(math.radians(lat))
    side_km = math.sqrt(area_ha * 10000) / 1000
    half_lat = side_km / km_per_deg_lat / 2
    half_lon = side_km / km_per_deg_lon / 2

    coords = [
        [lon - half_lon, lat - half_lat],
        [lon + half_lon, lat - half_lat],
        [lon + half_lon, lat + half_lat],
        [lon - half_lon, lat + half_lat],
        [lon - half_lon, lat - half_lat],
    ]
    return json.dumps({"type": "Polygon", "coordinates": [coords]})
