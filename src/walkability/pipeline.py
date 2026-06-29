from __future__ import annotations

import logging
from typing import Any

import geopandas as gpd


def run_one_city_pipeline(
    city_name: str,
    city_polygons: gpd.GeoDataFrame,
    categories: list[dict],
    cell_size: float,
    *,
    load_city_fn,
    create_hex_grid_fn,
    load_pois_fn,
    compute_accessibility_fn,
    export_results_fn,
    logger: logging.Logger | None = None,
) -> tuple[gpd.GeoDataFrame, tuple[Any, Any, Any, Any, Any]]:
    """
    Run one-city accessibility orchestration from prepared dependencies.

    Designed as a small callable entrypoint for smoke testing and future CLI use.
    """
    log = logger or logging.getLogger(__name__)

    log.info("Processing city: %s", city_name)
    boundary, graph, target_crs, city_polygon_wgs84 = load_city_fn(city_name, city_polygons)

    grid = create_hex_grid_fn(boundary, cell_size, target_crs)

    for category in categories:
        category_id = category["id"]
        log.info("Starting category: %s", category_id)
        pois = load_pois_fn(city_polygon_wgs84, category, target_crs)
        grid = compute_accessibility_fn(
            grid=grid,
            graph=graph,
            pois=pois,
            category_id=category_id,
            target_crs=target_crs,
        )

    export_paths = export_results_fn(city_name, grid, graph)
    return grid, export_paths

