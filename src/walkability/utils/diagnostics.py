from __future__ import annotations

import numpy as np
import pandas as pd


def build_accessibility_debug_summary(grid: pd.DataFrame, categories: list[dict]) -> pd.DataFrame:
    """
    Build a per-category diagnostics table to explain zero-minute travel times.
    """
    rows = []
    total_hexes = len(grid)

    for category in categories:
        category_id = category["id"]
        walk_min_col = f"{category_id}_walk_min"
        walk_m_col = f"{category_id}_walk_m"
        source_flag_col = f"{category_id}_is_source_node"
        source_count_col = f"{category_id}_source_poi_count_on_node"

        if walk_min_col not in grid.columns:
            continue

        walk_min_series = grid[walk_min_col]
        valid_mask = walk_min_series.notna()
        zero_mask = valid_mask & (walk_min_series == 0)

        source_mask = (
            grid[source_flag_col].fillna(False).astype(bool)
            if source_flag_col in grid.columns
            else pd.Series(False, index=grid.index)
        )

        zero_and_source_mask = zero_mask & source_mask

        source_counts = (
            grid[source_count_col].fillna(0)
            if source_count_col in grid.columns
            else pd.Series(0, index=grid.index)
        )

        walk_m_series = (
            grid[walk_m_col]
            if walk_m_col in grid.columns
            else pd.Series(np.nan, index=grid.index)
        )

        nearest_snap_series = (
            grid["nearest_node_snap_m"]
            if "nearest_node_snap_m" in grid.columns
            else pd.Series(np.nan, index=grid.index)
        )

        rows.append(
            {
                "category": category_id,
                "hex_count": total_hexes,
                "valid_hexes": int(valid_mask.sum()),
                "zero_min_hexes": int(zero_mask.sum()),
                "zero_min_pct": round(float(zero_mask.mean() * 100), 2) if total_hexes else 0.0,
                "source_node_hexes": int(source_mask.sum()),
                "zero_min_and_source_hexes": int(zero_and_source_mask.sum()),
                "zero_min_and_source_pct_of_zero": (
                    round(float((zero_and_source_mask.sum() / max(zero_mask.sum(), 1)) * 100), 2)
                    if zero_mask.sum() > 0
                    else 0.0
                ),
                "median_walk_m": round(float(walk_m_series[valid_mask].median()), 2)
                if valid_mask.any()
                else np.nan,
                "median_snap_m": round(float(nearest_snap_series.median()), 2)
                if nearest_snap_series.notna().any()
                else np.nan,
                "max_source_poi_count_on_node": int(source_counts.max()) if len(source_counts) else 0,
            }
        )

    summary_df = pd.DataFrame(rows)
    if summary_df.empty:
        return summary_df
    return summary_df.sort_values("category").reset_index(drop=True)

