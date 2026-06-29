from __future__ import annotations

import pandas as pd

from walkability.utils.diagnostics import build_accessibility_debug_summary


def test_build_accessibility_debug_summary_computes_expected_metrics() -> None:
    grid = pd.DataFrame(
        {
            "grocery_walk_min": [0.0, 10.0, 0.0, None],
            "grocery_walk_m": [0.0, 720.0, 0.0, None],
            "grocery_is_source_node": [True, False, False, False],
            "grocery_source_poi_count_on_node": [2, 0, 0, 0],
            "nearest_node_snap_m": [1.0, 2.0, 3.0, 4.0],
        }
    )
    categories = [{"id": "grocery"}]

    summary = build_accessibility_debug_summary(grid, categories)

    assert len(summary) == 1
    row = summary.iloc[0]
    assert row["category"] == "grocery"
    assert row["hex_count"] == 4
    assert row["valid_hexes"] == 3
    assert row["zero_min_hexes"] == 2
    assert row["zero_min_pct"] == 50.0
    assert row["source_node_hexes"] == 1
    assert row["zero_min_and_source_hexes"] == 1
    assert row["zero_min_and_source_pct_of_zero"] == 50.0
    assert row["median_walk_m"] == 0.0
    assert row["median_snap_m"] == 2.5
    assert row["max_source_poi_count_on_node"] == 2


def test_build_accessibility_debug_summary_skips_missing_category_columns() -> None:
    grid = pd.DataFrame({"other_walk_min": [1.0, 2.0]})
    categories = [{"id": "grocery"}]

    summary = build_accessibility_debug_summary(grid, categories)

    assert summary.empty

