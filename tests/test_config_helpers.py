from __future__ import annotations

from pathlib import Path

import pytest

from walkability.utils.config_helpers import load_configured_cities


def test_load_configured_cities_returns_ordered_names(tmp_path: Path) -> None:
    project_root = tmp_path / "urban-accessibility-analysis"
    notebooks_dir = project_root / "notebooks"
    config_dir = project_root / "config"
    notebooks_dir.mkdir(parents=True)
    config_dir.mkdir(parents=True)

    config_file = config_dir / "germany.yaml"
    config_file.write_text(
        """
name: Germany
cities:
  - name: Berlin
    lat: 52.52
    lon: 13.405
  - name: Munich
    lat: 48.137
    lon: 11.575
""".strip(),
        encoding="utf-8",
    )

    result = load_configured_cities("config/germany.yaml", cwd=notebooks_dir, country_name="germany")
    assert result == ["Berlin", "Munich"]


def test_load_configured_cities_raises_when_empty(tmp_path: Path) -> None:
    project_root = tmp_path / "urban-accessibility-analysis"
    notebooks_dir = project_root / "notebooks"
    config_dir = project_root / "config"
    notebooks_dir.mkdir(parents=True)
    config_dir.mkdir(parents=True)

    config_file = config_dir / "empty.yaml"
    config_file.write_text("name: Empty\ncities: []\n", encoding="utf-8")

    with pytest.raises(ValueError) as exc:
        load_configured_cities("config/empty.yaml", cwd=notebooks_dir)

    assert "No cities found" in str(exc.value)

