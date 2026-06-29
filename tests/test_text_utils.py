from __future__ import annotations

from walkability.boundaries import city_slug


def test_city_slug_transliterates_german_characters() -> None:
    assert city_slug("München") == "muenchen"
    assert city_slug("Straße") == "strasse"


def test_city_slug_strips_non_alnum_to_hyphens() -> None:
    assert city_slug("Quebec City") == "quebec-city"
    assert city_slug("  St. John's  ") == "st-john-s"


def test_city_slug_handles_non_string_input() -> None:
    assert city_slug(123) == ""

