from __future__ import annotations

import logging
from types import SimpleNamespace

import geopandas as gpd
import walkability.city_loader as city_loader
from shapely.geometry import Polygon


class _FakeGraph:
    def __init__(self):
        self.graph = {"crs": "EPSG:3857"}
        self._nodes = [1, 2, 3]
        self._edges = [(1, 2), (2, 3)]

    def nodes(self):
        return self._nodes

    def edges(self):
        return self._edges


class _FakeOx:
    def __init__(self):
        self.graph = _FakeGraph()

    def graph_from_polygon(self, polygon, **kwargs):
        return self.graph

    def project_graph(self, graph):
        return graph

    def features_from_polygon(self, polygon, tags):
        return gpd.GeoDataFrame(geometry=[], crs="EPSG:4326")


def test_load_city_raises_lookup_error_when_city_not_found() -> None:
    city_polygons = gpd.GeoDataFrame(
        {"city": ["Berlin"], "geometry": [Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])]},
        crs="EPSG:4326",
    )

    try:
        city_loader.load_city("Munich", city_polygons)
        raise AssertionError("Expected LookupError")
    except LookupError as exc:
        message = str(exc)
        assert "Munich" in message
        assert "Berlin" in message


def test_load_city_returns_projected_boundary_and_graph(monkeypatch) -> None:
    city_polygons = gpd.GeoDataFrame(
        {"city": ["Berlin"], "geometry": [Polygon([(13.3, 52.4), (13.3, 52.6), (13.5, 52.6), (13.5, 52.4)])]},
        crs="EPSG:4326",
    )

    fake_ox = _FakeOx()
    monkeypatch.setattr(city_loader, "ox", fake_ox)
    monkeypatch.setattr(city_loader, "nx", SimpleNamespace(weakly_connected_components=lambda g: [{1, 2}, {3}]))

    boundary, graph, target_crs, city_polygon_wgs84 = city_loader.load_city(
        "Berlin",
        city_polygons,
        logger=logging.getLogger("test_city_loader"),
    )

    assert target_crs == "EPSG:3857"
    assert str(boundary.crs).upper().endswith("3857")
    assert graph is fake_ox.graph
    assert city_polygon_wgs84 is not None

