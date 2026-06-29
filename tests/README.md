# Test Scaffold

This folder contains the refactor safety net for moving notebook logic into `src/walkability` modules.

## Current status

- Active baseline tests:
  - `test_notebook_integrity.py`
  - `test_text_utils.py`
  - `test_paths_utils.py`
  - `test_config_helpers.py`
  - `test_osm_utils.py`
  - `test_geometry_utils.py`
  - `test_diagnostics_utils.py`
  - `test_city_loader.py`
  - `test_poi_loader.py`
  - `test_accessibility.py`
  - `test_exporters.py`
  - `test_grids.py`
  - `test_pipeline_runner.py`
  - `test_pipeline_smoke_one_city.py`
- Scaffold placeholders (module-level skips):
  - None

As utility extraction progresses, replace placeholder skips with real assertions.

