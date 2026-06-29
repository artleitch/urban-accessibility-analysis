from __future__ import annotations

import logging

import geopandas as gpd
import numpy as np
from shapely.geometry import Point

from walkability.accessibility import compute_accessibility


def test_compute_accessibility_returns_nan_column_when_no_pois() -> None:
    grid = gpd.GeoDataFrame(geometry=[Point(0, 0), Point(1, 1)], crs="EPSG:3857")
    pois = gpd.GeoDataFrame(geometry=[], crs="EPSG:3857")

    result = compute_accessibility(
        grid=grid,
        graph=object(),
        pois=pois,
        category_id="grocery",
        target_crs="EPSG:3857",
        logger=logging.getLogger("test_accessibility"),
    )

    assert "grocery_walk_min" in result.columns
    assert result["grocery_walk_min"].isna().all()


def test_compute_accessibility_populates_walk_and_debug_columns() -> None:
    grid = gpd.GeoDataFrame(geometry=[Point(0, 0), Point(10, 0)], crs="EPSG:3857")
    pois = gpd.GeoDataFrame(geometry=[Point(0, 0)], crs="EPSG:3857")

    nodes = gpd.GeoDataFrame(
        geometry=[Point(0, 0), Point(10, 0)],
        index=[100, 200],
        crs="EPSG:3857",
    )
    edges = gpd.GeoDataFrame(geometry=[], crs="EPSG:3857")

    def fake_graph_to_gdfs(graph):
        return nodes, edges

    def fake_nearest_nodes(graph, X, Y):
        n = len(list(X))
        if n == 2:
            return [100, 200]
        return [100]

    def fake_dijkstra(graph, sources, weight):
        assert sources == [100]
        assert weight == "length"
        return {100: 0.0, 200: 144.0}

    result = compute_accessibility(
        grid=grid,
        graph=object(),
        pois=pois,
        category_id="grocery",
        target_crs="EPSG:3857",
        logger=logging.getLogger("test_accessibility"),
        graph_to_gdfs_fn=fake_graph_to_gdfs,
        nearest_nodes_fn=fake_nearest_nodes,
        multi_source_dijkstra_fn=fake_dijkstra,
    )

    assert np.isclose(result.loc[0, "grocery_walk_m"], 0.0)
    assert np.isclose(result.loc[1, "grocery_walk_m"], 144.0)
    assert np.isclose(result.loc[0, "grocery_walk_min"], 0.0)
    assert np.isclose(result.loc[1, "grocery_walk_min"], 2.0)

    assert result.loc[0, "grocery_source_poi_count_on_node"] == 1
    assert result.loc[1, "grocery_source_poi_count_on_node"] == 0
    assert bool(result.loc[0, "grocery_is_source_node"]) is True
    assert bool(result.loc[1, "grocery_is_source_node"]) is False
    assert "nearest_node_id" in result.columns
    assert "nearest_node_snap_m" in result.columns

