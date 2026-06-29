from __future__ import annotations

import gzip
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

import geopandas as gpd
import osmnx as ox


def export_results(
    city_name: str,
    grid: gpd.GeoDataFrame,
    graph: Any,
    *,
    include_network_debug_columns_in_export: bool,
    accessibility_output_relative: Path,
    frontend_public_relative: Path,
    city_slug_fn: Callable[[str], str],
    resolve_output_dir_fn: Callable[[Path], Path],
    resolve_project_file_fn: Callable[[Path], Path],
    logger: logging.Logger | None = None,
    graph_to_gdfs_fn: Callable[[Any], tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]] | None = None,
    copy_fn: Callable[[Path, Path], Any] | None = None,
) -> tuple[Path, Path, Path, Path, Path]:
    """
    Export accessibility outputs and optional frontend copies for one city.
    """
    log = logger or logging.getLogger(__name__)
    graph_to_gdfs = graph_to_gdfs_fn or ox.graph_to_gdfs

    if copy_fn is None:
        import shutil

        copy_fn = shutil.copy2

    log.info("Exporting results for %s", city_name)

    export_columns = [
        col for col in grid.columns if str(col) == "geometry" or str(col).endswith("_walk_min")
    ]

    if include_network_debug_columns_in_export:
        export_columns.extend(
            [
                col
                for col in grid.columns
                if str(col) in {"nearest_node_id", "nearest_node_snap_m"}
                or str(col).endswith("_walk_m")
                or str(col).endswith("_is_source_node")
                or str(col).endswith("_source_poi_count_on_node")
            ]
        )

    export_columns = list(dict.fromkeys(export_columns))
    export_grid = grid[export_columns].copy()

    output_dir = resolve_output_dir_fn(accessibility_output_relative)
    city_slug = city_slug_fn(city_name)

    gpkg_file = output_dir / f"{city_slug}_accessibility.gpkg"
    export_grid.to_file(gpkg_file, layer="accessibility", driver="GPKG")
    log.info("GeoPackage written: %s", gpkg_file)

    geojson_file = output_dir / f"{city_slug}_accessibility.geojson"
    export_grid.to_crs("EPSG:4326").to_file(geojson_file, driver="GeoJSON")
    log.info("GeoJSON written: %s", geojson_file)

    gzipped_file = Path(str(geojson_file) + ".gz")
    with open(geojson_file, "rb") as src, gzip.open(gzipped_file, "wb") as dst:
        dst.writelines(src)
    log.info("Gzipped GeoJSON written: %s", gzipped_file)

    network_nodes, network_edges = graph_to_gdfs(graph)

    network_edges_file = output_dir / f"{city_slug}_network_edges.geojson"
    network_edges.to_crs("EPSG:4326").to_file(network_edges_file, driver="GeoJSON")
    log.info("Network edges GeoJSON written: %s", network_edges_file)

    network_nodes_file = output_dir / f"{city_slug}_network_nodes.geojson"
    network_nodes.to_crs("EPSG:4326").to_file(network_nodes_file, driver="GeoJSON")
    log.info("Network nodes GeoJSON written: %s", network_nodes_file)

    try:
        frontend_public = resolve_project_file_fn(frontend_public_relative)
        frontend_dest = frontend_public / f"{city_slug}_accessibility.geojson"
        copy_fn(geojson_file, frontend_dest)
        log.info("Copied GeoJSON to frontend: %s", frontend_dest)

        frontend_network_edges_dest = frontend_public / f"{city_slug}_network_edges.geojson"
        copy_fn(network_edges_file, frontend_network_edges_dest)
        log.info("Copied network edges to frontend: %s", frontend_network_edges_dest)

        frontend_network_nodes_dest = frontend_public / f"{city_slug}_network_nodes.geojson"
        copy_fn(network_nodes_file, frontend_network_nodes_dest)
        log.info("Copied network nodes to frontend: %s", frontend_network_nodes_dest)
    except FileNotFoundError:
        log.warning(
            "frontend/public directory not found - skipping frontend copy. "
            "Manually copy %s, %s, and %s to serve them in the map app.",
            geojson_file,
            network_edges_file,
            network_nodes_file,
        )

    return gpkg_file, geojson_file, gzipped_file, network_edges_file, network_nodes_file

