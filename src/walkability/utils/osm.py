from __future__ import annotations

import logging
import time
from collections.abc import Callable, Sequence
from typing import Any

import osmnx as ox


def configure_osmnx_network_settings(
    request_timeout_seconds: int,
    *,
    overpass_rate_limit: bool = True,
) -> None:
    """
    Configure OSMnx request settings for resilient Overpass access.
    """
    ox.settings.requests_timeout = request_timeout_seconds
    ox.settings.overpass_rate_limit = overpass_rate_limit


def fetch_features_with_retry(
    city_polygon_wgs84: Any,
    tags: dict[str, Any],
    category_id: str,
    *,
    overpass_urls: Sequence[str],
    max_retries_per_endpoint: int,
    backoff_base_seconds: int,
    logger: logging.Logger,
    sleep_fn: Callable[[float], None] = time.sleep,
):
    """
    Fetch OSM features with retries and endpoint failover.
    Returns a GeoDataFrame-like object or None when all attempts fail.
    """
    original_overpass_url = ox.settings.overpass_url
    last_error: Exception | None = None

    try:
        for overpass_url in overpass_urls:
            ox.settings.overpass_url = overpass_url

            for attempt in range(1, max_retries_per_endpoint + 1):
                try:
                    logger.info(
                        "POI fetch '%s' via %s (attempt %d/%d)",
                        category_id,
                        overpass_url,
                        attempt,
                        max_retries_per_endpoint,
                    )
                    return ox.features_from_polygon(city_polygon_wgs84, tags)
                except Exception as exc:  # noqa: BLE001 - preserve notebook behavior
                    last_error = exc
                    message = str(exc)
                    timed_out = (
                        "ConnectTimeout" in message
                        or "ReadTimeout" in message
                        or "timed out" in message.lower()
                    )

                    if timed_out and attempt < max_retries_per_endpoint:
                        wait_seconds = backoff_base_seconds * attempt
                        logger.warning(
                            "Timeout for '%s' on %s; retrying in %ss",
                            category_id,
                            overpass_url,
                            wait_seconds,
                        )
                        sleep_fn(wait_seconds)
                        continue

                    logger.warning(
                        "POI fetch failed for '%s' on %s: %s",
                        category_id,
                        overpass_url,
                        exc,
                    )
                    break

        logger.error(
            "All Overpass attempts failed for '%s'. Last error: %s",
            category_id,
            last_error,
        )
        return None
    finally:
        ox.settings.overpass_url = original_overpass_url

