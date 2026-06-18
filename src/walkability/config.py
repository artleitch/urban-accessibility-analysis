"""
config.py — loads per-country YAML configs into a simple Python object.
"""

import yaml
from pathlib import Path


class CountryConfig:
    def __init__(self, data: dict):
        self.name = data["name"]
        self.boundary_file = data.get("boundary_file")
        self.census_file = data.get("census_file")
        self.join_key_boundary = data.get("join_key_boundary")
        self.join_key_census = data.get("join_key_census")
        self.population_col = data.get("population_col")
        self.crs = data.get("crs")
        self.census_read_csv_options = data.get("census_read_csv_options", {})
        self.census_filters = data.get("census_filters", {})
        self.filters = data["filters"]  # Keep as dict for direct access like config.filters["key"]
        self.clip_radius_km = data.get("clip_radius_km", 50)
        self.cities = data["cities"]  # list of dicts: name, region, lat, lon

    def __repr__(self):
        return f"<CountryConfig {self.name}: {len(self.cities)} cities>"


def load_config(country: str, config_dir: str = "config") -> CountryConfig:
    """
    Load a country config by name, e.g. load_config("australia")
    """
    path = Path(config_dir) / f"{country.lower()}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"No config found at {path}")
    with open(path) as f:
        data = yaml.safe_load(f)
    return CountryConfig(data)
