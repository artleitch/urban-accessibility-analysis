from __future__ import annotations

from shapely.geometry import LineString

from walkability.utils.geometry import create_points_along_line


def test_create_points_along_line_expected_count() -> None:
    line = LineString([(0, 0), (100, 0)])
    points = create_points_along_line(line, spacing=25)

    # Distances: 0, 25, 50, 75
    assert len(points) == 4


def test_create_points_along_line_starts_at_origin() -> None:
    line = LineString([(0, 0), (60, 0)])
    points = create_points_along_line(line, spacing=50)

    assert points[0].x == 0
    assert points[0].y == 0


def test_create_points_along_line_handles_short_lines() -> None:
    line = LineString([(0, 0), (10, 0)])
    points = create_points_along_line(line, spacing=50)

    # np.arange(0, 10, 50) yields only distance=0
    assert len(points) == 1

