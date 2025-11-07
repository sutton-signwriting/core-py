"""
pytest suite for the parse functions.
"""

from __future__ import annotations

import pytest

# ------------------------------------------------------------------ #
# Import the public API
# ------------------------------------------------------------------ #
from sutton_signwriting_core import (
    style_parse,
    style_compose,
    style_rgb_to_hex,
    style_rgba_to_hex,
    style_merge,
)


# ------------------------------------------------------------------ #
# Style Parsing Tests
# ------------------------------------------------------------------ #


@pytest.mark.parametrize(
    "style_str,expected",
    [
        ("-C", {"colorize": True}),
        ("-P10", {"padding": 10}),
        ("-G_000000_", {"background": "#000000"}),
        ("-D_FF0000_", {"detail": ["#FF0000"]}),
        ("-Z2", {"zoom": 2}),
        ("--D01_FF0000_", {"detailsym": [{"index": 1, "detail": ["#FF0000"]}]}),
        ("----class1 class2!", {"classes": "-class1 class2"}),
        ("---!id1!", {"id": "id1"}),
        (
            "-CP10G_000000_D_FF0000_Z2-D01_FF0000_--class1 class2!id1!",
            {
                "colorize": True,
                "padding": 10,
                "background": "#000000",
                "detail": ["#FF0000"],
                "zoom": 2,
                "detailsym": [{"index": 1, "detail": ["#FF0000"]}],
                "classes": "-class1 class2",
                "id": "id1",
            },
        ),
    ],
)
def test_style_parse(style_str, expected):
    assert style_parse(style_str) == expected


@pytest.mark.parametrize("invalid_style", ["", "-X", "invalid"])
def test_style_parse_invalid(invalid_style):
    assert style_parse(invalid_style) == {}


# ------------------------------------------------------------------ #
# Style Compose Tests
# ------------------------------------------------------------------ #


@pytest.mark.parametrize(
    "style_obj,expected",
    [
        ({"colorize": True}, "-C"),
        ({"padding": 10}, "-P10"),
        ({"background": "#000000"}, "-G_000000_"),
        ({"detail": ["#FF0000"]}, "-D_FF0000_"),
        ({"zoom": 2}, "-Z2"),
        ({"detailsym": [{"index": 1, "detail": ["#FF0000"]}]}, "--D01_FF0000_"),
        ({"classes": "-class1 class2"}, "----class1 class2!"),
        ({"id": "id1"}, "---!id1!"),
        (
            {
                "colorize": True,
                "padding": 10,
                "background": "#000000",
                "detail": ["#FF0000"],
                "zoom": 2,
                "detailsym": [{"index": 1, "detail": ["#FF0000"]}],
                "classes": "-class1 class2",
                "id": "id1",
            },
            "-CP10G_000000_D_FF0000_Z2-D01_FF0000_--class1 class2!id1!",
        ),
    ],
)
def test_style_compose(style_obj, expected):
    assert style_compose(style_obj) == expected


# ------------------------------------------------------------------ #
# Style RGB Tests
# ------------------------------------------------------------------ #


def test_style_rgb_to_hex():
    assert style_rgb_to_hex("rgb(0,0,0)") == "000000"
    assert style_rgb_to_hex("rgb(1,1,1)") == "010101"
    assert style_rgb_to_hex("rgb(255,255,255)") == "ffffff"
    assert style_rgb_to_hex("rgba(255,255,255,1)") == "ffffff"
    assert style_rgb_to_hex("rgba(255,255,255,0.5)") == "ffffff"
    assert style_rgb_to_hex("rgba(255,255,255,0)") == "transparent"
    assert style_rgb_to_hex("rgba(255,255,255,0.5)", 0.5) == "transparent"


def test_style_rgba_to_hex():
    assert style_rgba_to_hex("rgba(0,0,0,0)", "rgb(255,255,255)") == "transparent"
    assert style_rgba_to_hex("rgba(0,0,0,0.5)", "rgb(255,255,255)") == "7f7f7f"
    assert style_rgba_to_hex("rgba(0,0,0,1)", "rgb(255,255,255)") == "000000"
    assert style_rgba_to_hex("rgba(255,255,255,0)", "rgb(0,0,0)") == "transparent"
    assert style_rgba_to_hex("rgba(255,255,255,0.5)", "rgb(0,0,0)") == "7f7f7f"
    assert style_rgba_to_hex("rgba(255,255,255,1)", "rgb(0,0,0)") == "ffffff"
    assert style_rgba_to_hex("rgba(255,0,0,0.3)", "rgb(0,0,0)") == "4c0000"
    assert style_rgba_to_hex("rgba(0,255,0,0.3)", "rgb(0,0,0)") == "004c00"
    assert style_rgba_to_hex("rgba(0,0,255,0.3)", "rgb(0,0,0)") == "00004c"
    assert style_rgba_to_hex("rgb(255,255,255)", "rgb(0,0,0)") == "ffffff"


# ------------------------------------------------------------------ #
# Style Merge Tests
# ------------------------------------------------------------------ #
def test_merge_style_object():
    assert style_merge({"colorize": True}, {"zoom": 2}) == {"colorize": True, "zoom": 2}


def test_merge_bad_data():
    assert style_merge("a", "b") == {"zoom": 1}
