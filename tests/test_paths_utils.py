from __future__ import annotations

from pathlib import Path

import pytest

from walkability.utils.paths import resolve_output_dir, resolve_project_file


def test_resolve_project_file_finds_file_from_nested_notebook_like_cwd(tmp_path: Path) -> None:
    project_root = tmp_path / "urban-accessibility-analysis"
    notebooks_dir = project_root / "notebooks"
    data_dir = project_root / "data" / "processed"
    notebooks_dir.mkdir(parents=True)
    data_dir.mkdir(parents=True)

    target_file = data_dir / "germany_cities.gpkg"
    target_file.write_text("dummy", encoding="utf-8")

    resolved = resolve_project_file(Path("data/processed/germany_cities.gpkg"), cwd=notebooks_dir)
    assert resolved == target_file.resolve()


def test_resolve_project_file_raises_with_checked_paths(tmp_path: Path) -> None:
    project_root = tmp_path / "urban-accessibility-analysis"
    notebooks_dir = project_root / "notebooks"
    notebooks_dir.mkdir(parents=True)

    with pytest.raises(FileNotFoundError) as exc:
        resolve_project_file("missing/file.txt", cwd=notebooks_dir)

    message = str(exc.value)
    assert "Project file not found" in message
    assert "Current working directory" in message


def test_resolve_output_dir_creates_directory(tmp_path: Path) -> None:
    project_root = tmp_path / "urban-accessibility-analysis"
    notebooks_dir = project_root / "notebooks"
    parent_output = project_root / "data" / "processed"

    notebooks_dir.mkdir(parents=True)
    parent_output.mkdir(parents=True)

    output_dir = resolve_output_dir("data/processed/accessibility", cwd=notebooks_dir)
    assert output_dir == (parent_output / "accessibility").resolve()
    assert output_dir.exists()
    assert output_dir.is_dir()

