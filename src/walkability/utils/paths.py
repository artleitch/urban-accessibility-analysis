from __future__ import annotations

from pathlib import Path


def resolve_project_file(relative_path: str | Path, cwd: Path | None = None) -> Path:
    """
    Resolve a project file from common notebook execution locations.

    The lookup checks the provided cwd (or current working directory),
    one parent level, and then each ancestor joined with the relative path.
    """
    rel_path = Path(relative_path)
    base_cwd = cwd or Path.cwd()

    candidates = [
        base_cwd / rel_path,
        base_cwd / ".." / rel_path,
    ]

    for parent in [base_cwd, *base_cwd.parents]:
        candidates.append(parent / rel_path)

    seen: set[str] = set()
    unique_candidates: list[Path] = []
    for candidate in candidates:
        resolved = candidate.resolve()
        key = str(resolved)
        if key not in seen:
            seen.add(key)
            unique_candidates.append(resolved)

    for candidate in unique_candidates:
        if candidate.exists():
            return candidate

    tried = "\n".join(f" - {path}" for path in unique_candidates)
    raise FileNotFoundError(
        f"Project file not found: {rel_path}\n"
        f"Checked:\n{tried}\n"
        f"Current working directory: {base_cwd}"
    )


def resolve_output_dir(relative_path: str | Path, cwd: Path | None = None) -> Path:
    """
    Resolve and create an output directory inside the project.
    """
    rel_path = Path(relative_path)
    output_dir = resolve_project_file(rel_path.parent, cwd=cwd) / rel_path.name
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

