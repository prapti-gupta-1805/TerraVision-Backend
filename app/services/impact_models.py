def estimate_tree_impact(trees_added):
    return {
        "co2_absorbed_tons": trees_added * 0.021,
        "aqi_drop": trees_added * 0.002
    }


def estimate_ev_impact(ev_percent):
    return {
        "co2_reduction_pct": ev_percent * 0.6
    }


def estimate_solar_impact(kw):
    return {
        "co2_saved_tons": kw * 0.0012
    }