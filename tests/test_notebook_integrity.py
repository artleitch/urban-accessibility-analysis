from __future__ import annotations

import ast
import json
from pathlib import Path


NOTEBOOK_PATHS = [
    Path("notebooks/001_accessibility_pipeline.ipynb"),
    Path("notebooks/002_boundary_density_generator.ipynb"),
]


def _load_notebook(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _code_for_ast(nb: dict) -> str:
    chunks: list[str] = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue

        source = cell.get("source", "")
        if isinstance(source, list):
            text = "".join(source)
        else:
            text = str(source)

        filtered_lines = []
        for line in text.splitlines():
            stripped = line.lstrip()
            if stripped.startswith("%") or stripped.startswith("!"):
                continue
            filtered_lines.append(line)

        chunks.append("\n".join(filtered_lines))

    return "\n\n".join(chunks)


def test_notebooks_are_valid_json() -> None:
    for path in NOTEBOOK_PATHS:
        nb = _load_notebook(path)
        assert isinstance(nb, dict), f"Notebook must load as dict: {path}"
        assert "cells" in nb, f"Notebook missing cells key: {path}"


def test_notebook_code_cells_parse_with_ast() -> None:
    for path in NOTEBOOK_PATHS:
        nb = _load_notebook(path)
        code = _code_for_ast(nb)
        ast.parse(code, filename=str(path))

