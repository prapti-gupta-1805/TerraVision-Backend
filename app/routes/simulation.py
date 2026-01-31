from fastapi import APIRouter
from app.services.geo_processing import geojson_to_shape, polygon_area_km2
from app.services.impact_models import (
    estimate_tree_impact,
    estimate_ev_impact,
    estimate_solar_impact
)

router = APIRouter(prefix="/simulation", tags=["simulation"])


@router.post("/run")
def run_simulation(payload: dict):

    geom = geojson_to_shape(payload["area"])
    area_km2 = polygon_area_km2(geom)

    trees = payload.get("trees_added", 0)
    ev_pct = payload.get("ev_percent", 0)
    solar_kw = payload.get("solar_kw", 0)

    tree = estimate_tree_impact(trees)
    ev = estimate_ev_impact(ev_pct)
    solar = estimate_solar_impact(solar_kw)

    return {
        "area_km2": area_km2,
        "tree_impact": tree,
        "ev_impact": ev,
        "solar_impact": solar
    }