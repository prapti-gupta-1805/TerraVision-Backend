from shapely.geometry import shape

def geojson_to_shape(geojson_obj):
    return shape(geojson_obj["geometry"] if geojson_obj["type"] == "Feature" else geojson_obj)


def polygon_area_km2(geom):
    # rough planar approximation — fine for hackathon
    return geom.area * 111 * 111