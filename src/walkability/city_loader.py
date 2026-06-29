from __future__ import annotations

import logging
from typing import Any

import geopandas as gpd
import networkx as nx
import osmnx as ox


def load_city(
    city_name: str,
    city_polygons: gpd.GeoDataFrame,
    *,
    network_type: str = "walk",
    retain_all_components: bool = True,
    truncate_by_edge: bool = True,
    logger: logging.Logger | None = None,
) -> tuple[gpd.GeoDataFrame, Any, Any, Any]:
    """
    Load and prepare a city boundary and walk graph.

    Returns:
        boundary (GeoDataFrame in projected CRS),
        graph (OSMnx graph in projected CRS),
        target_crs,
        city_polygon_wgs84 (unioned polygon used for OSM queries).
    """
    log = logger or logging.getLogger(__name__)

    log.info("Loading city data for %s", city_name)

    match = city_polygons[city_polygons["city"].str.lower() == city_name.lower()].copy()

    if match.empty:
        available = ", ".join(city_polygons["city"].astype(str).sort_values().unique())
        raise LookupError(f"City '{city_name}' not found in city polygons. Available: {available}")

    boundary = match[["geometry"]].copy()
    if boundary.crs is None:
        raise ValueError("City polygon layer has no CRS defined")

    boundary_wgs84 = boundary.to_crs("EPSG:4326")
    city_polygon_wgs84 = boundary_wgs84.union_all()
    log.debug("Boundary loaded from polygon file: %d feature(s)", boundary.shape[0])

    graph = ox.graph_from_polygon(
        city_polygon_wgs84,
        network_type=network_type,
        retain_all=retain_all_components,
        truncate_by_edge=truncate_by_edge,
    )
    graph = ox.project_graph(graph)

    component_sizes = sorted(
        (len(component) for component in nx.weakly_connected_components(graph)),
        reverse=True,
    )
    n_components = len(component_sizes)
    largest_component_nodes = component_sizes[0] if component_sizes else 0

    log.debug("Graph loaded: %d nodes, %d edges", len(graph.nodes()), len(graph.edges()))
    log.info(
        "Network diagnostics: components=%d, largest_component_nodes=%d, retain_all=%s, truncate_by_edge=%s",
        n_components,
        largest_component_nodes,
        retain_all_components,
        truncate_by_edge,
    )

    target_crs = graph.graph["crs"]

    boundary = boundary.to_crs(target_crs)
    log.debug("Boundary reprojected to %s", target_crs)

    water = ox.features_from_polygon(city_polygon_wgs84, {"natural": "water"})

    if water.empty:
        log.info("No water features found in polygon extent")
    else:
        water = water.to_crs(target_crs)
        water_union = water.union_all()
        log.debug("Water features loaded and unioned")

        boundary["geometry"] = boundary.geometry.difference(water_union)
        log.info("City boundary cleaned by removing water areas")

    return boundary, graph, target_crs, city_polygon_wgs84

