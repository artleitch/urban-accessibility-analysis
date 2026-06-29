from __future__ import annotations

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Polygon


def create_hex_grid(boundary: gpd.GeoDataFrame, cell_size: float, crs) -> gpd.GeoDataFrame:
    """
    Create a clipped hex grid and centroid helper column for a city boundary.
    """

    def hexagon(center_x: float, center_y: float, radius: float) -> Polygon:
        angles = np.arange(0, 360, 60) + 30
        return Polygon(
            [
                (
                    center_x + radius * np.cos(np.radians(angle)),
                    center_y + radius * np.sin(np.radians(angle)),
                )
                for angle in angles
            ]
        )

    def create_hex_grid_internal(boundary_gdf: gpd.GeoDataFrame, size: float) -> gpd.GeoDataFrame:
        minx, miny, maxx, maxy = boundary_gdf.total_bounds

        radius = size
        dx = np.sqrt(3) * radius
        dy = 1.5 * radius

        polygons: list[Polygon] = []

        row = 0
        y = miny

        while y <= maxy + dy:
            x_offset = (dx / 2) if row % 2 else 0
            x = minx + x_offset

            while x <= maxx + dx:
                polygons.append(hexagon(x, y, radius))
                x += dx

            y += dy
            row += 1

        return gpd.GeoDataFrame(geometry=polygons, crs=boundary_gdf.crs)

    hex_grid = create_hex_grid_internal(boundary, cell_size)

    boundary_union = boundary.union_all()

    inside_mask = hex_grid.geometry.within(boundary_union)
    intersects_mask = hex_grid.geometry.intersects(boundary_union)

    inside_hexes = hex_grid[inside_mask].copy()
    edge_hexes = hex_grid[intersects_mask & ~inside_mask].copy()

    if not edge_hexes.empty:
        edge_hexes["geometry"] = edge_hexes.geometry.intersection(boundary_union)
        edge_hexes = edge_hexes[~edge_hexes.geometry.is_empty].copy()

    hex_grid = gpd.GeoDataFrame(
        pd.concat([inside_hexes, edge_hexes], ignore_index=True),
        geometry="geometry",
        crs=crs,
    )

    hex_grid["centroid"] = hex_grid.geometry.centroid
    return hex_grid

