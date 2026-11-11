"""Tests for multi-dash range patterns (e.g. "5-3-1")."""

import pytest

from mangadex_downloader.range import InvalidPattern, compile


def test_multi_dash_pattern_raises_invalid_pattern():
    with pytest.raises(InvalidPattern):
        compile("5-3-1")


def test_valid_ranges_still_compile():
    assert compile("1-5") is not None
    assert compile("1-") is not None
    assert compile("-5") is not None
