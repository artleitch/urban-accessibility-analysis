from __future__ import annotations

import logging
from typing import Any, Callable

import geopandas as gpd
import pandas as pd


def load_pois(
    city_polygon_wgs84: Any,
    category: dict,
    target_crs: Any,
    *,
    fetch_features_fn: Callable[[Any, dict, str], Any],
    create_points_along_line_fn: Callable[[Any, float], list],
    logger: logging.Logger | None = None,
) -> gpd.GeoDataFrame:
    """
    Load POIs for a category and normalize output to point geometries.

    For polygon-based categories, polygon boundaries are sampled into points.
    """
    log = logger or logging.getLogger(__name__)

    category_id = category["id"]
    log.info("Loading POIs for category '%s'", category_id)

    tags = category["tags"]
    use_polygons = category["usePolygons"]

    raw_pois = fetch_features_fn(city_polygon_wgs84, tags, category_id)
    if raw_pois is None or raw_pois.empty:
        log.warning("No POIs found for category '%s'", category_id)
        return gpd.GeoDataFrame(geometry=[], crs=target_crs)

    pois = raw_pois.to_crs(target_crs)
    log.debug("Raw POI count for %s: %d", category_id, len(pois))

    if not use_polygons:
        pois = pois[pois.geometry.type == "Point"].copy()
        log.info("Loaded %d point POIs for category '%s'", len(pois), category_id)
        return pois

    log.info("Category '%s' uses polygon processing", category_id)

    point_features = pois[pois.geometry.type == "Point"].copy()
    polygon_features = pois[pois.geometry.type.isin(["Polygon", "MultiPolygon"])].copy()
    log.debug("Found %d polygon features for category '%s'", len(polygon_features), category_id)

    polygon_features["area_m2"] = polygon_features.area
    polygon_features = polygon_features[polygon_features["area_m2"] >= 5000]
    log.info("Filtered to %d large polygons for '%s'", len(polygon_features), category_id)

    boundary_points: list[Any] = []
    for geom in polygon_features.geometry:
        boundary = geom.boundary

        if boundary.geom_type == "LineString":
            boundary_points.extend(create_points_along_line_fn(boundary, spacing=50))
        elif boundary.geom_type == "MultiLineString":
            for line in boundary.geoms:
                boundary_points.extend(create_points_along_line_fn(line, spacing=50))

    boundary_points_gdf = gpd.GeoDataFrame(geometry=boundary_points, crs=target_crs)
    log.debug(
        "Created %d sampled boundary points for '%s'",
        len(boundary_points_gdf),
        category_id,
    )

    combined = pd.concat(
        [
            point_features[["geometry"]],
            boundary_points_gdf,
        ],
        ignore_index=True,
    )
    log.info("Returning %d total POI geometries for category '%s'", len(combined), category_id)

    return gpd.GeoDataFrame(combined, geometry="geometry", crs=target_crs)

