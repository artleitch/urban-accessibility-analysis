"""
boundaries.py — core pipeline for deriving city urban-extent polygons
from sub-city census boundaries + population data.

Pipeline per city:
  1. Clip national boundary layer to a radius around the city centroid
  2. Calculate area + population density per unit
  3. Filter to dense units only
  4. Buffer + dissolve to connect nearby dense units into clusters
  5. Re-join original units to each cluster to recover real population
  6. Apply city-level population + area filters
  7. Return pass/fail + the resulting polygon
"""

import geopandas as gpd
import pandas as pd
import re
import unicodedata
from shapely.geometry import Point
from typing import cast


# Default metric CRS used when a country-specific one is not provided.
DEFAULT_METRIC_CRS = "EPSG:3577"


def normalize_german_city_name(name: str) -> str:
    """Apply German transliteration first, then remove remaining diacritics."""
    if not isinstance(name, str):
        return name

    replacements = {
        "Ä": "Ae",
        "Ö": "Oe",
        "Ü": "Ue",
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss",
    }
    for source, target in replacements.items():
        name = name.replace(source, target)

    name = unicodedata.normalize("NFKD", name)
    return "".join(ch for ch in name if not unicodedata.combining(ch))


def city_slug(name: str) -> str:
    """Create a lowercase ASCII slug from a city name."""
    if not isinstance(name, str):
        return ""
    normalized = normalize_german_city_name(name).lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    return re.sub(r"-{2,}", "-", normalized)


def load_boundaries_with_population(
    boundary_path: str,
    census_path: str,
    boundary_join_col: str,
    census_join_col: str,
    population_col: str,
    census_read_csv_options: dict | None = None,
    census_filters: dict | None = None,
) -> gpd.GeoDataFrame:
    """
    Load the SA2 (or equivalent) boundary shapefile, join census population,
    and return a single GeoDataFrame with a clean 'population' column.
    """
    gdf = gpd.read_file(boundary_path)
    census = cast(
        pd.DataFrame,
        pd.read_csv(
            filepath_or_buffer=census_path,
            **(census_read_csv_options or {}),
        ),
    )

    # Normalize headers (trim whitespace / BOM) to avoid fragile join-key lookups.
    gdf.columns = [str(col).strip().lstrip("\ufeff") for col in gdf.columns]
    census.columns = [str(col).strip().lstrip("\ufeff") for col in census.columns]

    if boundary_join_col not in gdf.columns:
        raise KeyError(
            f"Boundary join column '{boundary_join_col}' not found. "
            f"Available boundary columns: {list(gdf.columns)}"
        )

    if census_join_col not in census.columns:
        raise KeyError(
            f"Census join column '{census_join_col}' not found. "
            f"Available census columns: {list(census.columns)}"
        )

    if population_col not in census.columns:
        raise KeyError(
            f"Population column '{population_col}' not found. "
            f"Available census columns: {list(census.columns)}"
        )

    if census_filters:
        for column, expected_value in census_filters.items():
            if isinstance(expected_value, list):
                census = census[census[column].isin(expected_value)].copy()
            else:
                census = census[census[column] == expected_value].copy()

    # Normalise join keys to string to avoid int/str mismatches
    gdf[boundary_join_col] = gdf[boundary_join_col].astype(str)
    census[census_join_col] = census[census_join_col].astype(str)

    merged = gdf.merge(
        census[[census_join_col, population_col]],
        left_on=boundary_join_col,
        right_on=census_join_col,
        how="left",
    )
    merged = merged.rename(columns={population_col: "population"})

    n_missing = merged["population"].isna().sum()
    if n_missing > 0:
        print(f"⚠️  Warning: {n_missing} units have no population match after join")

    return gpd.GeoDataFrame(merged, geometry="geometry", crs=gdf.crs)


def calculate_density(
    gdf: gpd.GeoDataFrame,
    metric_crs: str = DEFAULT_METRIC_CRS,
) -> gpd.GeoDataFrame:
    """
    Reproject to a metric CRS, calculate area_km2 and pop_density.
    Returns a new GeoDataFrame in the requested metric CRS.
    """
    gdf_metric = gdf.to_crs(metric_crs)
    gdf_metric["area_km2"] = gdf_metric.geometry.area / 1_000_000
    gdf_metric["pop_density"] = gdf_metric["population"] / gdf_metric["area_km2"]
    return gdf_metric


def clip_to_city(
    gdf_metric: gpd.GeoDataFrame,
    lat: float,
    lon: float,
    radius_km: float,
    metric_crs: str | None = None,
) -> gpd.GeoDataFrame:
    """
    Clip the national layer to all units whose geometry intersects a circle
    of `radius_km` around the (lat, lon) city centroid.
    """
    # Build the centre point in WGS84, then reproject to metric CRS for buffering
    target_crs = metric_crs or gdf_metric.crs or DEFAULT_METRIC_CRS
    centre = gpd.GeoDataFrame(
        {"geometry": [Point(lon, lat)]}, crs="EPSG:4326"
    ).to_crs(target_crs)

    circle = centre.geometry.iloc[0].buffer(radius_km * 1000)  # km -> m

    clipped = gdf_metric[gdf_metric.geometry.intersects(circle)].copy()
    return clipped


def filter_dense_units(
    gdf_clipped: gpd.GeoDataFrame,
    density_threshold: float = 1000,
) -> gpd.GeoDataFrame:
    """
    Keep only units above the density threshold (people / km2).
    """
    return gdf_clipped[gdf_clipped["pop_density"] > density_threshold].copy()


def dissolve_clusters(
    dense_units: gpd.GeoDataFrame,
    buffer_m: float = 500,
) -> gpd.GeoDataFrame:
    """
    Buffer dense units, dissolve overlapping ones into clusters, then
    return the dissolved cluster polygons (NOT yet re-joined to original
    unit population data — that happens in `summarise_clusters`).

    Each resulting row is one contiguous urban cluster, with a unique
    cluster_id.
    """
    buffered = dense_units.copy()
    buffered["geometry"] = dense_units.geometry.buffer(buffer_m)

    # Dissolve all overlapping buffered geometries into single multi-part rows,
    # then explode so each contiguous cluster is its own row
    dissolved = buffered.dissolve()
    exploded = dissolved.explode(index_parts=False).reset_index(drop=True)
    exploded["cluster_id"] = exploded.index

    return exploded[["cluster_id", "geometry"]]


def summarise_clusters(
    dense_units: gpd.GeoDataFrame,
    dissolved_clusters: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """
    Spatially join the original (un-buffered) dense units back to each
    dissolved cluster, then aggregate population and area per cluster.

    Returns one row per cluster with: cluster_id, population, area_km2,
    pop_density, geometry (the dissolved/buffered cluster shape).
    """
    # Use centroids of original units to assign them to a cluster — avoids
    # edge ambiguity from intersecting buffered boundaries
    units_with_centroid = dense_units.copy()
    units_with_centroid["centroid"] = units_with_centroid.geometry.centroid

    centroid_gdf = gpd.GeoDataFrame(
        units_with_centroid.drop(columns="geometry").rename(
            columns={"centroid": "geometry"}
        ),
        geometry="geometry",
        crs=dense_units.crs,
    )

    joined = gpd.sjoin(
        centroid_gdf,
        dissolved_clusters,
        how="left",
        predicate="within",
    )

    agg = (
        joined.groupby("cluster_id")
        .agg(population=("population", "sum"), area_km2=("area_km2", "sum"))
        .reset_index()
    )
    agg["pop_density"] = agg["population"] / agg["area_km2"]

    result = dissolved_clusters.merge(agg, on="cluster_id", how="left")
    return gpd.GeoDataFrame(result, geometry="geometry", crs=dissolved_clusters.crs)


def apply_city_filters(
    clusters: gpd.GeoDataFrame,
    min_population: float,
    min_area_km2: float,
) -> gpd.GeoDataFrame:
    """
    Apply the city-level pass/fail filters and add a 'passes_filter' column
    rather than silently dropping — useful for logging.
    """
    clusters = clusters.copy()
    clusters["passes_filter"] = (
        (clusters["population"] >= min_population)
        & (clusters["area_km2"] >= min_area_km2)
    )
    return clusters


def process_city(
    gdf_metric: gpd.GeoDataFrame,
    city: dict,
    clip_radius_km: float,
    density_threshold: float,
    min_population: float,
    min_area_km2: float,
    buffer_m: float = 500,
    metric_crs: str | None = None,
) -> dict:
    """
    Run the full pipeline for a single city config entry.
    Returns a result dict with the log info and the resulting GeoDataFrame
    of clusters (pass + fail, for inspection).
    """
    name = city["name"]
    lat, lon = city["lat"], city["lon"]

    clipped = clip_to_city(gdf_metric, lat, lon, clip_radius_km, metric_crs=metric_crs)

    if clipped.empty:
        return {
            "name": name,
            "status": "no_units_found",
            "clusters": None,
        }

    dense = filter_dense_units(clipped, density_threshold)

    if dense.empty:
        return {
            "name": name,
            "status": "no_dense_units",
            "clusters": None,
        }

    dissolved = dissolve_clusters(dense, buffer_m)
    summarised = summarise_clusters(dense, dissolved)
    filtered = apply_city_filters(summarised, min_population, min_area_km2)

    # The "winning" cluster is the largest contiguous one that passes
    passing = filtered[filtered["passes_filter"]]
    if passing.empty:
        status = "filtered_out"
    else:
        status = "passed"

    return {
        "name": name,
        "name_ascii": normalize_german_city_name(name),
        "city_slug": city_slug(name),
        "status": status,
        "clusters": filtered,  # all clusters, pass + fail, for inspection
    }
