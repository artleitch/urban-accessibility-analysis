from __future__ import annotations

import logging
from pathlib import Path

import yaml

from .paths import resolve_project_file


def load_configured_cities(
    country_config_relative: str | Path,
    *,
    cwd: Path | None = None,
    country_name: str | None = None,
    logger: logging.Logger | None = None,
) -> list[str]:
    """
    Load city names from a country YAML config file.

    The path is resolved from notebook-like working directories using
    ``resolve_project_file``.
    """
    config_file = resolve_project_file(country_config_relative, cwd=cwd)
    label = country_name or Path(country_config_relative).stem

    if logger:
        logger.info("Using %s config file: %s", str(label).title(), config_file)

    with open(config_file, encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    configured_cities = [city["name"] for city in config.get("cities", [])]
    if not configured_cities:
        raise ValueError(f"No cities found in {config_file}")

    if logger:
        logger.info(
            "Loaded %d configured cities from %s YAML",
            len(configured_cities),
            str(label).title(),
        )

    return configured_cities

