## Plan: Notebook Utilities Extraction (Pass 1)

Create a root planning doc and execute a low-risk extraction that moves notebook methods into `src/walkability` modules, aggregated via package exports. Keep pipeline defaults (`COUNTRY`, `categories`, `cell_size`, output relative paths) in the notebook while making execution helpers testable in Python modules.

### Current Execution Status
1. [x] Root plan file created (`plan-notebookUtilsExtraction.prompt.md`).
2. [x] Utility package scaffold created in [`src/walkability/utils/`](src/walkability/utils/).
3. [x] Shared utility modules extracted and exported via package aggregators.
4. [x] Notebook utility cells updated to import extracted helpers (with thin wrappers where constants stay in notebook).
5. [x] Test scaffold implemented and activated for extracted utility modules.
6. [x] Core graph/POI/export modules extracted in pass 2 (`load_city`, `load_pois`, `compute_accessibility`, `export_results`).
7. [x] Non-critical notebook methods extracted (`create_hex_grid`).
8. [x] Callable one-city pipeline entrypoint added for smoke testing.
9. [x] Optional notebook cleanup completed (wrapper reduction + import pruning).

### Test-First Refactor Guardrails
1. Add `pytest` tests for each moved utility before replacing notebook `def` blocks.
2. Keep behavior parity tests by snapshotting expected outputs for representative inputs.
3. Add notebook integrity checks: JSON load + code-cell AST parse.
4. Add a one-city dry-run smoke test to the export stage (small scope city from config).
5. Require green test run before and after each extraction batch.

### Methods to Move (Shared Utilities Only)
1. [x] `city_name_to_slug` -> unified to `walkability.boundaries.city_slug` via notebook wrapper.
2. [x] `resolve_project_file` -> [`src/walkability/utils/paths.py`](src/walkability/utils/paths.py)
3. [x] `resolve_output_dir` -> [`src/walkability/utils/paths.py`](src/walkability/utils/paths.py)
4. [x] `load_configured_cities` -> [`src/walkability/utils/config_helpers.py`](src/walkability/utils/config_helpers.py)
5. [x] `configure_osmnx_network_settings` -> [`src/walkability/utils/osm.py`](src/walkability/utils/osm.py)
6. [x] `fetch_features_with_retry` -> [`src/walkability/utils/osm.py`](src/walkability/utils/osm.py)
7. [x] `create_points_along_line` -> [`src/walkability/utils/geometry.py`](src/walkability/utils/geometry.py)
8. [x] `build_accessibility_debug_summary` -> [`src/walkability/utils/diagnostics.py`](src/walkability/utils/diagnostics.py)

### Decisions Captured
1. Unify slug generation with `walkability.boundaries.city_slug` (single shared implementation).
2. Root canonical plan filename can be deferred for now.
3. In pass 2, prioritize extraction of graph/POI logic before export-layer extraction.

### Test Suite Status
1. [x] `tests/test_text_utils.py`
   - `city_slug` normalization parity for German transliterations and ASCII cleanup.
2. [x] `tests/test_paths_utils.py`
   - `resolve_project_file` finds files from notebook and project-root working directories.
   - `resolve_output_dir` creates directories deterministically.
3. [x] `tests/test_config_helpers.py`
   - `load_configured_cities` returns ordered city names and fails cleanly on empty city lists.
4. [x] `tests/test_osm_utils.py`
   - `configure_osmnx_network_settings` applies timeout/rate-limit settings.
   - `fetch_features_with_retry` retries and rotates endpoints (mock `osmnx` calls).
5. [x] `tests/test_geometry_utils.py`
   - `create_points_along_line` spacing/point-count expectations for known line lengths.
6. [x] `tests/test_diagnostics_utils.py`
   - `build_accessibility_debug_summary` computes stable counts/percentages from fixture grid.
7. [x] `tests/test_notebook_integrity.py`
   - `notebooks/001_accessibility_pipeline.ipynb` and `notebooks/002_boundary_density_generator.ipynb` JSON load.
   - Combined code cells parse with `ast.parse`.
8. [x] `tests/test_pipeline_smoke_one_city.py`
   - Minimal one-city runner reaches export stage.
9. [x] `tests/test_grids.py`
   - `create_hex_grid` returns clipped cells with centroid helper column.
10. [x] `tests/test_pipeline_runner.py`
   - Callable one-city runner reaches export stage with injected fakes.

### Latest Validation Snapshot
1. Latest full test run: `31 passed`.
2. No active placeholder skips remain.

### Validation Gates Per Refactor PR
1. Unit tests for moved functions pass.
2. Notebook integrity tests pass.
3. One-city smoke test executed or explicitly deferred with reason.
4. No output schema drift for `_walk_min` fields and export filenames.

### Remaining Work (Next)
1. No required refactor items remain from this plan.
2. Future improvements are optional and can be tracked as a new follow-up plan.

### Pass 2 Progress
1. [x] Added [`src/walkability/city_loader.py`](src/walkability/city_loader.py) with `load_city`.
2. [x] Added `tests/test_city_loader.py` for missing-city and successful load behavior.
3. [x] Added [`src/walkability/poi_loader.py`](src/walkability/poi_loader.py) with `load_pois`.
4. [x] Added `tests/test_poi_loader.py` for empty, point-only, and polygon-sampling behavior.
5. [x] Added [`src/walkability/accessibility.py`](src/walkability/accessibility.py) with `compute_accessibility`.
6. [x] Added `tests/test_accessibility.py` for empty POI and deterministic distance-mapping behavior.
7. [x] Added [`src/walkability/exporters.py`](src/walkability/exporters.py) with `export_results`.
8. [x] Added `tests/test_exporters.py` for export column selection and frontend-copy behavior.
9. [x] Added [`src/walkability/grids.py`](src/walkability/grids.py) with `create_hex_grid`.
10. [x] Added [`src/walkability/pipeline.py`](src/walkability/pipeline.py) with `run_one_city_pipeline` callable entrypoint.
11. [x] Updated [`notebooks/001_accessibility_pipeline.ipynb`](notebooks/001_accessibility_pipeline.ipynb) wrappers to use module implementations for moved methods.
