from __future__ import annotations

import logging

import geopandas as gpd
from shapely.geometry import Point, Polygon

from walkability.poi_loader import load_pois


def test_load_pois_returns_empty_when_fetch_fails() -> None:
    category = {"id": "grocery", "tags": {"shop": ["supermarket"]}, "usePolygons": False}

    result = load_pois(
        city_polygon_wgs84=Polygon([(0, 0), (0, 1), (1, 1), (1, 0)]),
        category=category,
        target_crs="EPSG:3857",
        fetch_features_fn=lambda *_: None,
        create_points_along_line_fn=lambda line, spacing=50: [],
        logger=logging.getLogger("test_poi_loader"),
    )

    assert result.empty


def test_load_pois_point_category_filters_to_points() -> None:
    raw = gpd.GeoDataFrame(
        geometry=[Point(0, 0), Point(1, 1), Polygon([(0, 0), (0, 2), (2, 2), (2, 0)])],
        crs="EPSG:4326",
    )
    category = {"id": "libraries", "tags": {"amenity": ["library"]}, "usePolygons": False}

    result = load_pois(
        city_polygon_wgs84=Polygon([(0, 0), (0, 1), (1, 1), (1, 0)]),
        category=category,
        target_crs="EPSG:3857",
        fetch_features_fn=lambda *_: raw,
        create_points_along_line_fn=lambda line, spacing=50: [],
        logger=logging.getLogger("test_poi_loader"),
    )

    assert len(result) == 2
    assert set(result.geometry.type.unique()) == {"Point"}


def test_load_pois_polygon_category_samples_boundaries() -> None:
    polygon = Polygon([(0, 0), (0, 100), (100, 100), (100, 0)])
    raw = gpd.GeoDataFrame(
        geometry=[Point(1, 1), polygon],
        crs="EPSG:3857",
    )
    category = {"id": "parks", "tags": {"leisure": ["park"]}, "usePolygons": True}

    sampled = [Point(0, 0), Point(0, 50), Point(0, 100)]

    result = load_pois(
        city_polygon_wgs84=Polygon([(0, 0), (0, 1), (1, 1), (1, 0)]),
        category=category,
        target_crs="EPSG:3857",
        fetch_features_fn=lambda *_: raw,
        create_points_along_line_fn=lambda line, spacing=50: sampled,
        logger=logging.getLogger("test_poi_loader"),
    )

    assert len(result) == 1 + len(sampled)
    assert set(result.geometry.type.unique()) == {"Point"}

