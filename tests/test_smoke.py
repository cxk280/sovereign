"""Smoke test — establishes the pytest gate for the verification ladder.

Later build-order steps replace/extend this with real unit and property tests.
"""

import sovereign


def test_version_is_importable() -> None:
    assert isinstance(sovereign.__version__, str)
