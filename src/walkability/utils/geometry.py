from __future__ import annotations

import numpy as np


def create_points_along_line(line, spacing: float = 50):
    """
    Create points every ``spacing`` metres along a LineString-like geometry.
    """
    distances = np.arange(0, line.length, spacing)
    return [line.interpolate(distance) for distance in distances]

