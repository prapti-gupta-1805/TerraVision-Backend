import requests
from datetime import datetime
import xml.etree.ElementTree as ET
from fastapi import APIRouter
from app.db.firebase_client import db

router = APIRouter(prefix="/aqi", tags=["aqi"])


@router.get("/")
def get_aqi():

    url = "https://airquality.cpcb.gov.in/caaqms/rss_feed"

    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=15)

    root = ET.fromstring(r.content)

    results = []

    for state in root.findall(".//State"):
        state_name = state.attrib.get("id")

        for city in state.findall("City"):
            city_name = city.attrib.get("id")

            for station in city.findall("Station"):

                station_data = {
                    "state": state_name,
                    "city": city_name,
                    "station": station.attrib.get("id"),
                    "updated": station.attrib.get("lastupdate"),
                    "lat": station.attrib.get("latitude"),
                    "lon": station.attrib.get("longitude"),
                    "pollutants": {}
                }

                for p in station.findall("Pollutant_Index"):
                    pid = p.attrib.get("id")
                    station_data["pollutants"][pid] = {
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

@router.post("/")
def store_aqi():

    url = "https://airquality.cpcb.gov.in/caaqms/rss_feed"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=15)

    root = ET.fromstring(r.content)

    stored = 0

    for state in root.findall(".//State"):
        state_name = state.attrib.get("id")

        for city in state.findall("City"):
            city_name = city.attrib.get("id")

            for station in city.findall("Station"):

                doc = {
                    "state": state_name,
                    "city": city_name,
                    "station": station.attrib.get("id"),
                    "updated": station.attrib.get("lastupdate"),
                    "lat": float(station.attrib.get("latitude")),
                    "lon": float(station.attrib.get("longitude")),
                    "pollutants": {},
                    "source": "CPCB",
                    "created_at": datetime.utcnow()
                }

                for p in station.findall("Pollutant_Index"):
                    pid = p.attrib.get("id")
                    doc["pollutants"][pid] = {
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
