from __future__ import annotations

import logging
from types import SimpleNamespace

import walkability.utils.osm as osm_utils


class _FakeOx:
    def __init__(self, responses):
        self.settings = SimpleNamespace(
            requests_timeout=0,
            overpass_rate_limit=False,
            overpass_url="https://original.endpoint/api",
        )
        self._responses = list(responses)
        self.calls: list[tuple[object, dict]] = []

    def features_from_polygon(self, polygon, tags):
        self.calls.append((polygon, tags))
        next_item = self._responses.pop(0)
        if isinstance(next_item, Exception):
            raise next_item
        return next_item


def test_configure_osmnx_network_settings_updates_ox_settings(monkeypatch) -> None:
    fake_ox = _FakeOx(responses=[])
    monkeypatch.setattr(osm_utils, "ox", fake_ox)

    osm_utils.configure_osmnx_network_settings(300, overpass_rate_limit=True)

    assert fake_ox.settings.requests_timeout == 300
    assert fake_ox.settings.overpass_rate_limit is True


def test_fetch_features_with_retry_succeeds_after_timeout_retry(monkeypatch) -> None:
    fake_ox = _FakeOx(
        responses=[
            Exception("ReadTimeout while contacting server"),
            {"ok": True},
        ]
    )
    monkeypatch.setattr(osm_utils, "ox", fake_ox)

    waits: list[float] = []
    logger = logging.getLogger("test_osm_utils")

    result = osm_utils.fetch_features_with_retry(
        city_polygon_wgs84=object(),
        tags={"amenity": ["library"]},
        category_id="libraries",
        overpass_urls=["https://a/api"],
        max_retries_per_endpoint=2,
        backoff_base_seconds=5,
        logger=logger,
        sleep_fn=waits.append,
    )

    assert result == {"ok": True}
    assert waits == [5]
    assert fake_ox.settings.overpass_url == "https://original.endpoint/api"


def test_fetch_features_with_retry_returns_none_after_all_failures(monkeypatch) -> None:
    fake_ox = _FakeOx(
        responses=[
            Exception("ConnectTimeout during request"),
            Exception("service unavailable"),
        ]
    )
    monkeypatch.setattr(osm_utils, "ox", fake_ox)

    logger = logging.getLogger("test_osm_utils")
    result = osm_utils.fetch_features_with_retry(
        city_polygon_wgs84=object(),
        tags={"shop": ["supermarket"]},
        category_id="grocery",
        overpass_urls=["https://a/api", "https://b/api"],
        max_retries_per_endpoint=1,
        backoff_base_seconds=5,
        logger=logger,
        sleep_fn=lambda _: None,
    )

    assert result is None
    assert fake_ox.settings.overpass_url == "https://original.endpoint/api"

