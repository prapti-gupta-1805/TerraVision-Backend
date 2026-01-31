from app.services.geo_filter import buffer_1km, filter_features
from fastapi import APIRouter
import json
from fastapi import APIRouter
from shapely.geometry import Point, shape
from pyproj import Transformer
from shapely.ops import transform

router = APIRouter(prefix="/geo", tags=["geo"])

@router.get("/solar")
def solar_within_radius(lat: float, lon: float):

    with open("data/solar_panels.geojson", encoding="utf-8") as f:
        data = json.load(f)

    buffer_geom = buffer_1km(lat, lon)
    return filter_features(data["features"], buffer_geom)