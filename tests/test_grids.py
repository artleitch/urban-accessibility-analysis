from __future__ import annotations

import geopandas as gpd
from shapely.geometry import Polygon

from walkability.grids import create_hex_grid


def test_create_hex_grid_returns_cells_and_centroids() -> None:
    boundary = gpd.GeoDataFrame(
        geometry=[Polygon([(0, 0), (0, 500), (500, 500), (500, 0)])],
        crs="EPSG:3857",
    )

    grid = create_hex_grid(boundary=boundary, cell_size=100, crs="EPSG:3857")

    assert not grid.empty
    assert "centroid" in grid.columns
    assert str(grid.crs).upper().endswith("3857")
    assert grid.geometry.notna().all()


def test_create_hex_grid_is_clipped_to_boundary_extent() -> None:
    boundary = gpd.GeoDataFrame(
        geometry=[Polygon([(0, 0), (0, 300), (300, 300), (300, 0)])],
        crs="EPSG:3857",
    )

    grid = create_hex_grid(boundary=boundary, cell_size=80, crs="EPSG:3857")

    boundary_union = boundary.union_all()
    assert grid.geometry.intersects(boundary_union).all()

