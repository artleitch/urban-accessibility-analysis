# Copilot Skill: Urban Accessibility Analysis

Use these repository-specific rules when generating code, notebooks, and debugging suggestions.

## Project Context
- Primary workflow is in `notebooks/001_accessibility_pipeline.ipynb`.
- Geospatial stack: `geopandas`, `osmnx`, `networkx`, `shapely`, `numpy`, `pandas`, `pyyaml`.
- Country-specific city inputs come from `config/*.yaml` and `data/processed/*_cities.gpkg`.
- Frontend artifacts are copied to `frontend/public/*.geojson`.

## Coding Preferences
- Prefer small, composable functions over long monolithic cells.
- Keep Python indentation strictly 4 spaces.
- Use logging (not print) for pipeline diagnostics, except explicit tabular debug output.
- Preserve existing naming conventions (`city_polygon_wgs84`, `target_crs`, `walk_m_col`, etc.).
- Avoid breaking notebook execution order; add new helpers in separate `#%%` cells.

## Reliability and Performance
- Add retries for network/Overpass requests and log endpoint/attempt.
- Keep CRS handling explicit and consistent (`EPSG:4326` for OSM queries, projected CRS for distances).
- Prefer vectorized/geopandas operations over Python loops when practical.
- When processing many cities, include per-city timing and memory diagnostics.
- Explicitly free heavy objects and run garbage collection between city iterations.

## Data and Export Rules
- Preserve existing output formats:
  - GeoPackage: `data/processed/accessibility/{city_slug}_accessibility.gpkg`
  - GeoJSON: `data/processed/accessibility/{city_slug}_accessibility.geojson`
  - Frontend copies in `frontend/public/`
- Keep `_walk_min` as the primary final accessibility output field.
- Only include debug columns when `INCLUDE_NETWORK_DEBUG_COLUMNS_IN_EXPORT` is `True`.

## When Fixing Bugs
- Prioritize correctness of: city filtering, CRS transforms, nearest-node matching, and Dijkstra sources.
- Check for indentation and notebook-cell formatting issues first when syntax errors appear.
- Add lightweight validation steps after edits (JSON validity and Python AST parse of code cells).

## Tests and Validation
After changing notebook logic, run minimal checks:
1. Notebook JSON loads.
2. Combined code cells parse with Python AST.
3. One-city dry run completes to export stage.

If runtime checks are expensive, clearly state what was not executed and why.

