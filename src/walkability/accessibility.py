from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

import geopandas as gpd
import networkx as nx
import numpy as np
import osmnx as ox


def compute_accessibility(
    grid: gpd.GeoDataFrame,
    graph: Any,
    pois: gpd.GeoDataFrame,
    category_id: str,
    target_crs: Any,
    *,
    logger: logging.Logger | None = None,
    walking_speed_m_per_min: float = 72,
    graph_to_gdfs_fn: Callable[[Any], tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]] | None = None,
    nearest_nodes_fn: Callable[[Any, Any, Any], Any] | None = None,
    multi_source_dijkstra_fn: Callable[[Any, Any, str], dict[Any, float]] | None = None,
) -> gpd.GeoDataFrame:
    """
    Compute network distance from each grid cell to nearest POI for a category.
    """
    log = logger or logging.getLogger(__name__)
    graph_to_gdfs = graph_to_gdfs_fn or ox.graph_to_gdfs
    nearest_nodes = nearest_nodes_fn or ox.distance.nearest_nodes
    multi_source_dijkstra = multi_source_dijkstra_fn or nx.multi_source_dijkstra_path_length

    log.info("Computing accessibility for '%s'", category_id)
    walk_col = f"{category_id}_walk_min"
    walk_m_col = f"{category_id}_walk_m"
    source_flag_col = f"{category_id}_is_source_node"
    source_count_col = f"{category_id}_source_poi_count_on_node"

    if pois.empty:
        log.warning(
            "Skipping accessibility computation for '%s' because no POIs were found",
            category_id,
        )
        result = grid.copy()
        result[walk_col] = np.nan
        return result

    centroids = grid.copy()
    centroids["geometry"] = centroids.geometry.centroid
    centroids = centroids.set_geometry("geometry")
    centroids = centroids.to_crs(target_crs)
    log.debug("Centroids prepared: %d features; graph CRS=%s", len(centroids), target_crs)

    nodes, edges = graph_to_gdfs(graph)
    log.debug("Graph converted to GeoDataFrames: %d nodes, %d edges", len(nodes), len(edges))

    centroids["nearest_node"] = nearest_nodes(
        graph,
        X=centroids.geometry.x,
        Y=centroids.geometry.y,
    )

    nearest_node_geoms = centroids["nearest_node"].map(nodes.geometry)
    centroids["nearest_node_snap_m"] = centroids.geometry.distance(nearest_node_geoms)

    pois = pois.copy()
    pois["nearest_node"] = nearest_nodes(
        graph,
        X=pois.geometry.x,
        Y=pois.geometry.y,
    )
    log.debug("Nearest nodes matched for %d POIs", len(pois))

    source_nodes = list(pois["nearest_node"].unique())
    log.info("Using %d unique source nodes for '%s'", len(source_nodes), category_id)

    source_node_counts = pois["nearest_node"].value_counts()
    centroids[source_count_col] = centroids["nearest_node"].map(source_node_counts).fillna(0).astype(int)
    centroids[source_flag_col] = centroids[source_count_col] > 0

    distances = multi_source_dijkstra(
        graph,
        sources=source_nodes,
        weight="length",
    )

    result = grid.set_geometry("geometry")
    result = result.drop(
        columns=[
            col
            for col in result.columns
            if col != "geometry" and str(result[col].dtype) == "geometry"
        ]
    )
    log.debug("Cleaned up intermediate geometry columns for '%s'", category_id)

    result[walk_m_col] = centroids["nearest_node"].map(distances)
    result[walk_col] = result[walk_m_col] / walking_speed_m_per_min

    if "nearest_node_id" not in result.columns:
        result["nearest_node_id"] = centroids["nearest_node"].values
    if "nearest_node_snap_m" not in result.columns:
        result["nearest_node_snap_m"] = centroids["nearest_node_snap_m"].values

    result[source_count_col] = centroids[source_count_col].values
    result[source_flag_col] = centroids[source_flag_col].values

    zero_minutes = int((result[walk_col] == 0).sum())
    source_node_hexes = int(result[source_flag_col].sum())
    log.info(
        "Debug '%s': zero-minute hexes=%d, hexes snapped to POI source nodes=%d",
        category_id,
        zero_minutes,
        source_node_hexes,
    )
    log.info("Computed walk duration field '%s' for '%s'", walk_col, category_id)

    return result

