import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from fastapi import APIRouter

from shapely.geometry import Point, shape
from shapely.ops import transform
from pyproj import Transformer

from app.db.firebase_client import db

router = APIRouter(prefix="/aqi", tags=["aqi"])

CPCB_URL = "https://airquality.cpcb.gov.in/caaqms/rss_feed"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# -------------------------------
# GEO HELPERS (INLINE)
# -------------------------------

project = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:3857",
    always_xy=True
).transform


def buffer_1km(lat, lon):
    point = Point(lon, lat)
    point_m = transform(project, point)
    return point_m.buffer(1000)


def filter_geojson(features, buffer_geom):
    filtered = []

    for f in features:
        geom = shape(f["geometry"])
        geom_m = transform(project, geom)

        if geom_m.intersects(buffer_geom):
            filtered.append(f)

    return {
        "type": "FeatureCollection",
        "features": filtered
    }

# -------------------------------
# GET /aqi  (RAW JSON)
# -------------------------------

@router.get("/")
def get_aqi():

    r = requests.get(CPCB_URL, headers=HEADERS, timeout=15)
    root = ET.fromstring(r.content)

    results = []

    for state in root.findall(".//State"):
        for city in state.findall("City"):
            for station in city.findall("Station"):

                station_data = {
                    "state": state.attrib.get("id"),
                    "city": city.attrib.get("id"),
                    "station": station.attrib.get("id"),
                    "updated": station.attrib.get("lastupdate"),
                    "lat": station.attrib.get("latitude"),
                    "lon": station.attrib.get("longitude"),
                    "pollutants": {}
                }

                for p in station.findall("Pollutant_Index"):
                    station_data["pollutants"][p.attrib.get("id")] = {
                        "avg": p.attrib.get("Avg"),
                        "min": p.attrib.get("Min"),
                        "max": p.attrib.get("Max"),
                        "sub_index": p.attrib.get("Hourly_sub_index")
                    }

                results.append(station_data)

    return {
        "source": "CPCB XML",
        "stations": len(results),
        "data": results
    }

# -------------------------------
# POST /aqi  (STORE IN FIREBASE)
# -------------------------------

@router.post("/")
def store_aqi():

    r = requests.get(CPCB_URL, headers=HEADERS, timeout=15)
    root = ET.fromstring(r.content)

    stored = 0

    for state in root.findall(".//State"):
        for city in state.findall("City"):
            for station in city.findall("Station"):

                try:
                    lat = float(station.attrib.get("latitude"))
                    lon = float(station.attrib.get("longitude"))
                except (TypeError, ValueError):
                    continue

                doc = {
                    "state": state.attrib.get("id"),
                    "city": city.attrib.get("id"),
                    "station": station.attrib.get("id"),
                    "updated": station.attrib.get("lastupdate"),
                    "lat": lat,
                    "lon": lon,
                    "pollutants": {},
                    "source": "CPCB",
                    "created_at": datetime.utcnow()
                }

                for p in station.findall("Pollutant_Index"):
                    doc["pollutants"][p.attrib.get("id")] = {
                        "avg": p.attrib.get("Avg"),
                        "min": p.attrib.get("Min"),
                        "max": p.attrib.get("Max"),
                        "sub_index": p.attrib.get("Hourly_sub_index")
                    }

                db.collection("aqi_readings").add(doc)
                stored += 1

    return {
        "status": "stored",
        "documents_added": stored
    }

# -------------------------------
# AQI → GEOJSON
# -------------------------------

def aqi_to_geojson(aqi_data):
    features = []

    for s in aqi_data:
        try:
            lat = float(s["lat"])
            lon = float(s["lon"])
        except (TypeError, ValueError):
            continue

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat]
            },
            "properties": {
                "station": s["station"],
                "city": s["city"],
                "state": s["state"],
                "updated": s["updated"],
                "pollutants": s["pollutants"]
            }
        })

    return features

# -------------------------------
# GET /aqi/geojson
# -------------------------------

@router.get("/geojson")
def get_aqi_geojson(lat: float, lon: float):

    aqi_data = get_aqi()["data"]
    features = aqi_to_geojson(aqi_data)
    buffer_geom = buffer_1km(lat, lon)

    return filter_geojson(features, buffer_geom)
