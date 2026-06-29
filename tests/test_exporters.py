from __future__ import annotations

import logging
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point

from walkability.exporters import export_results


class _FakeGeoDataFrame(gpd.GeoDataFrame):
    _metadata = ["recorded_calls"]

    @property
    def _constructor(self):
        return _FakeGeoDataFrame


def _make_grid() -> _FakeGeoDataFrame:
    grid = _FakeGeoDataFrame(
        {
            "grocery_walk_min": [1.0],
            "grocery_walk_m": [72.0],
            "grocery_is_source_node": [False],
            "grocery_source_poi_count_on_node": [0],
            "nearest_node_id": [123],
            "nearest_node_snap_m": [5.5],
            "ignore_me": [999],
            "geometry": [Point(0, 0)],
        },
        crs="EPSG:3857",
    )
    grid.recorded_calls = []
    return grid


def test_export_results_selects_expected_columns_and_frontend_copies(monkeypatch, tmp_path: Path) -> None:
    grid = _make_grid()
    output_dir = tmp_path / "accessibility"
    frontend_dir = tmp_path / "frontend_public"
    output_dir.mkdir(parents=True)
    frontend_dir.mkdir(parents=True)

    def fake_to_file(self, filename, *args, **kwargs):
        self.recorded_calls.append((Path(filename), list(self.columns), kwargs))
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        Path(filename).write_text("{}", encoding="utf-8")

    monkeypatch.setattr(gpd.GeoDataFrame, "to_file", fake_to_file)

    nodes = _FakeGeoDataFrame({"geometry": [Point(0, 0)]}, crs="EPSG:3857")
    edges = _FakeGeoDataFrame({"geometry": [Point(0, 0)]}, crs="EPSG:3857")
    nodes.recorded_calls = []
    edges.recorded_calls = []

    copy_calls = []

    result = export_results(
        city_name="Berlin",
        grid=grid,
        graph=object(),
        include_network_debug_columns_in_export=True,
        accessibility_output_relative=Path("data/processed/accessibility"),
        frontend_public_relative=Path("frontend/public"),
        city_slug_fn=lambda _: "berlin",
        resolve_output_dir_fn=lambda _: output_dir,
        resolve_project_file_fn=lambda _: frontend_dir,
        logger=logging.getLogger("test_exporters"),
        graph_to_gdfs_fn=lambda _: (nodes, edges),
        copy_fn=lambda src, dst: copy_calls.append((Path(src), Path(dst))),
    )

    gpkg_file, geojson_file, gz_file, edges_file, nodes_file = result
    assert gpkg_file.name == "berlin_accessibility.gpkg"
    assert geojson_file.name == "berlin_accessibility.geojson"
    assert gz_file.name == "berlin_accessibility.geojson.gz"
    assert edges_file.name == "berlin_network_edges.geojson"
    assert nodes_file.name == "berlin_network_nodes.geojson"

    exported_columns = grid.recorded_calls[0][1]
    assert "grocery_walk_min" in exported_columns
    assert "grocery_walk_m" in exported_columns
    assert "grocery_is_source_node" in exported_columns
    assert "grocery_source_poi_count_on_node" in exported_columns
    assert "nearest_node_id" in exported_columns
    assert "nearest_node_snap_m" in exported_columns
    assert "ignore_me" not in exported_columns

    assert len(copy_calls) == 3
    assert copy_calls[0][1].name == "berlin_accessibility.geojson"


def test_export_results_skips_frontend_copy_when_dir_missing(monkeypatch, tmp_path: Path) -> None:
    grid = _make_grid()
    output_dir = tmp_path / "accessibility"
    output_dir.mkdir(parents=True)

    def fake_to_file(self, filename, *args, **kwargs):
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        Path(filename).write_text("{}", encoding="utf-8")

    monkeypatch.setattr(gpd.GeoDataFrame, "to_file", fake_to_file)

    nodes = gpd.GeoDataFrame({"geometry": [Point(0, 0)]}, crs="EPSG:3857")
    edges = gpd.GeoDataFrame({"geometry": [Point(0, 0)]}, crs="EPSG:3857")

    copies = []

    export_results(
        city_name="Berlin",
        grid=grid,
        graph=object(),
        include_network_debug_columns_in_export=False,
        accessibility_output_relative=Path("data/processed/accessibility"),
        frontend_public_relative=Path("frontend/public"),
        city_slug_fn=lambda _: "berlin",
        resolve_output_dir_fn=lambda _: output_dir,
        resolve_project_file_fn=lambda _: (_ for _ in ()).throw(FileNotFoundError("missing")),
        logger=logging.getLogger("test_exporters"),
        graph_to_gdfs_fn=lambda _: (nodes, edges),
        copy_fn=lambda src, dst: copies.append((src, dst)),
    )

    assert copies == []

