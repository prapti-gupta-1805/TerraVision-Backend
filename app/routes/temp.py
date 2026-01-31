import requests
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/temp", tags=["weather"])

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

@router.get("/")
def get_temperature(lat: float = 28.6139, lon: float = 77.2090):

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,apparent_temperature",
        "hourly": "temperature_2m,apparent_temperature",
        "timezone": "auto"
    }

    try:
        resp = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail="Weather API request failed")

    return resp.json()
