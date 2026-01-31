from shapely.geometry import Point, shape
from shapely.ops import transform
from pyproj import Transformer

# CRS transformers
project = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:3857",
    always_xy=True
).transform


def buffer_1km(lat, lon):
    """
    Create a 1km buffer (in meters) around a lat/lon point
    """
    point = Point(lon, lat)
    point_m = transform(project, point)
    return point_m.buffer(1000)  # meters


def filter_features(features, buffer_geom):
    """
    Filter GeoJSON features that intersect the buffer
    """
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
