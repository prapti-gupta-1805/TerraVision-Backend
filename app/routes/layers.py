from fastapi import APIRouter, HTTPException
import json
import os

router = APIRouter(prefix="/layers", tags=["layers"])

DATA_DIR = "data"


@router.get("/{layer_name}")
def get_layer(layer_name: str):
    file_path = os.path.join(DATA_DIR, f"{layer_name}.geojson")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Layer not found")

    with open(file_path, encoding="utf-8") as f:
        return json.load(f)