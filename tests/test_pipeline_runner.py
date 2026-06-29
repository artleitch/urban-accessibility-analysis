from __future__ import annotations

import logging
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point

from walkability.pipeline import run_one_city_pipeline


def test_run_one_city_pipeline_reaches_export_stage() -> None:
    city_polygons = gpd.GeoDataFrame(
        {"city": ["Berlin"], "geometry": [Point(0, 0).buffer(1)]},
        crs="EPSG:4326",
    )

    categories = [{"id": "grocery"}, {"id": "parks"}]

    def fake_load_city(city_name, polygons):
        boundary = gpd.GeoDataFrame(geometry=[Point(0, 0).buffer(10)], crs="EPSG:3857")
        return boundary, object(), "EPSG:3857", Point(0, 0).buffer(10)

    def fake_create_hex_grid(boundary, cell_size, crs):
        return gpd.GeoDataFrame(geometry=[Point(0, 0)], crs="EPSG:3857")

    def fake_load_pois(city_polygon_wgs84, category, target_crs):
        return gpd.GeoDataFrame(geometry=[Point(0, 0)], crs="EPSG:3857")

    def fake_compute_accessibility(grid, graph, pois, category_id, target_crs):
        grid = grid.copy()
        grid[f"{category_id}_walk_min"] = [1.0]
        return grid

    def fake_export_results(city_name, grid, graph):
        return (
            Path("dummy.gpkg"),
            Path("dummy.geojson"),
            Path("dummy.geojson.gz"),
            Path("dummy_edges.geojson"),
            Path("dummy_nodes.geojson"),
        )

    grid, export_paths = run_one_city_pipeline(
        city_name="Berlin",
        city_polygons=city_polygons,
        categories=categories,
        cell_size=100,
        load_city_fn=fake_load_city,
        create_hex_grid_fn=fake_create_hex_grid,
        load_pois_fn=fake_load_pois,
        compute_accessibility_fn=fake_compute_accessibility,
        export_results_fn=fake_export_results,
        logger=logging.getLogger("test_pipeline_runner"),
    )

    assert "grocery_walk_min" in grid.columns
    assert "parks_walk_min" in grid.columns
    assert len(export_paths) == 5

