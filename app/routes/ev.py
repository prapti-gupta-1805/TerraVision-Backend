from fastapi import APIRouter
import json

from app.services.geo_filter import buffer_1km, filter_features

router = APIRouter(prefix="/geo", tags=["geo"])


@router.get("/ev")
def ev_within_radius(lat: float, lon: float):

    with open("data/ev_charging_stations.geojson", encoding="utf-8") as f:
        data = json.load(f)

    buffer_geom = buffer_1km(lat, lon)
    return filter_features(data["features"], buffer_geom)
