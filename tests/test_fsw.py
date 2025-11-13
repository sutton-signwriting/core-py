"""
pytest suite for the structure functions.
"""

from __future__ import annotations

import pytest

# ------------------------------------------------------------------ #
# Import the public API
# ------------------------------------------------------------------ #
from sutton_signwriting_core import (
    fsw_is_type,
    fsw_colorize,
    fsw_parse_symbol,
    fsw_parse_sign,
    fsw_parse_text,
    fsw_compose_symbol,
    fsw_compose_sign,
    fsw_info,
    fsw_column_defaults_merge,
    fsw_columns,
    fsw_tokenize,
    fsw_detokenize,
    FSWTokenizer,
)


# ------------------------------------------------------------------ #
# Structure classification
# ------------------------------------------------------------------ #
def test_fsw_is_type():
    assert fsw_is_type("S10000", "hand") is True
    assert fsw_is_type("S20500", "movement") is True
    assert fsw_is_type("S38700", "punctuation") is True
    assert fsw_is_type("S00000", "hand") is False
    assert fsw_is_type("invalid", "hand") is False


# ------------------------------------------------------------------ #
# Colorize
# ------------------------------------------------------------------ #
def test_fsw_colorize_right_color():
    assert fsw_colorize("S10000") == "#0000CC"
    assert fsw_colorize("S20600") == "#CC0000"
    assert fsw_colorize("S2f700") == "#FF0099"
    assert fsw_colorize("S35d00") == "#006600"
    assert fsw_colorize("S36d00") == "#000000"
    assert fsw_colorize("S37f00") == "#884411"
    assert fsw_colorize("S38b00") == "#FF9900"
    assert fsw_colorize("S00000") == "#000000"


def test_fsw_colorize_bad_input():
    assert fsw_colorize(5) == "#000000"
    assert fsw_colorize(["what"]) == "#000000"


# ------------------------------------------------------------------ #
# FSW Parsing Tests
# ------------------------------------------------------------------ #


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("S10000", {"symbol": "S10000"}),
        ("S10000500x500", {"symbol": "S10000", "coord": [500, 500]}),
        ("S10000-C", {"symbol": "S10000", "style": "-C"}),
        ("S10000-Zx", {"symbol": "S10000", "style": "-Zx"}),
        (
            "S10000--D01_FF0000_",
            {"symbol": "S10000", "style": "--D01_FF0000_"},
        ),
        (
            "S10000-CD_green,red_-D01_red,blue_",
            {"symbol": "S10000", "style": "-CD_green,red_-D01_red,blue_"},
        ),
    ],
)
def test_fsw_parse_symbol(input_str, expected):
    assert fsw_parse_symbol(input_str) == expected


@pytest.mark.parametrize(
    "input_str, expected",
    [
        (
            "S10000-CD_green,red_G_yellow_",  # background (G) should be before detail (D)
            {"symbol": "S10000", "style": "-CD_green,red_"},
        ),
    ],
)
def test_fsw_parse_symbol_malformed_style(input_str, expected):
    assert fsw_parse_symbol(input_str) == expected


@pytest.mark.parametrize("invalid_input", ["a"])
def test_fsw_parse_symbol_invalid(invalid_input):
    assert fsw_parse_symbol(invalid_input) == {}


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("M500x500", {"box": "M", "max": [500, 500]}),
        (
            "M525x535S2e748483x510S10011501x466S2e704510x500S10019476x475",
            {
                "box": "M",
                "max": [525, 535],
                "spatials": [
                    {"symbol": "S2e748", "coord": [483, 510]},
                    {"symbol": "S10011", "coord": [501, 466]},
                    {"symbol": "S2e704", "coord": [510, 500]},
                    {"symbol": "S10019", "coord": [476, 475]},
                ],
            },
        ),
        (
            "AS10011S10019S2e704S2e748M525x535S2e748483x510S10011501x466S2e704510x500S10019476x475",
            {
                "sequence": ["S10011", "S10019", "S2e704", "S2e748"],
                "box": "M",
                "max": [525, 535],
                "spatials": [
                    {"symbol": "S2e748", "coord": [483, 510]},
                    {"symbol": "S10011", "coord": [501, 466]},
                    {"symbol": "S2e704", "coord": [510, 500]},
                    {"symbol": "S10019", "coord": [476, 475]},
                ],
            },
        ),
        (
            "AS10011S00000S2e704S2e748M525x535S2e748483x510S10011501x466S2e704510x500S10019476x475",
            {
                "sequence": ["S10011", "S00000", "S2e704", "S2e748"],
                "box": "M",
                "max": [525, 535],
                "spatials": [
                    {"symbol": "S2e748", "coord": [483, 510]},
                    {"symbol": "S10011", "coord": [501, 466]},
                    {"symbol": "S2e704", "coord": [510, 500]},
                    {"symbol": "S10019", "coord": [476, 475]},
                ],
            },
        ),
        (
            "AS10011S10019S2e704S2e748M525x535S2e748483x510S10011501x466S2e704510x500S10019476x475-C",
            {
                "sequence": ["S10011", "S10019", "S2e704", "S2e748"],
                "box": "M",
                "max": [525, 535],
                "spatials": [
                    {"symbol": "S2e748", "coord": [483, 510]},
                    {"symbol": "S10011", "coord": [501, 466]},
                    {"symbol": "S2e704", "coord": [510, 500]},
                    {"symbol": "S10019", "coord": [476, 475]},
                ],
                "style": "-C",
            },
        ),
        (
            "AS10011S10019S2e704S2e748M525x535S2e748483x510S10011501x466S2e704510x500S10019476x475-CD_green,red_-D01_red,blue_",
            {
                "sequence": ["S10011", "S10019", "S2e704", "S2e748"],
                "box": "M",
                "max": [525, 535],
                "spatials": [
                    {"symbol": "S2e748", "coord": [483, 510]},
                    {"symbol": "S10011", "coord": [501, 466]},
                    {"symbol": "S2e704", "coord": [510, 500]},
                    {"symbol": "S10019", "coord": [476, 475]},
                ],
                "style": "-CD_green,red_-D01_red,blue_",
            },
        ),
    ],
)
def test_fsw_parse_sign(input_str, expected):
    assert fsw_parse_sign(input_str) == expected


@pytest.mark.parametrize("invalid_input", ["a"])
def test_fsw_parse_sign_invalid(invalid_input):
    assert fsw_parse_sign(invalid_input) == {}


def test_fsw_parse_text_basic():
    assert fsw_parse_text(
        "AS14c20S27106M518x529S14c20481x471S27106503x489 AS18701S1870aS2e734S20500M518x533S1870a489x515S18701482x490S20500508x496S2e734500x468 S38800464x496"
    ) == [
        "AS14c20S27106M518x529S14c20481x471S27106503x489",
        "AS18701S1870aS2e734S20500M518x533S1870a489x515S18701482x490S20500508x496S2e734500x468",
        "S38800464x496",
    ]


def test_fsw_parse_text_with_style():
    assert fsw_parse_text(
        "AS14c20S27106M518x529S14c20481x471S27106503x489-C AS18701S1870aS2e734S20500M518x533S1870a489x515S18701482x490S20500508x496S2e734500x468 S38800464x496-Z2"
    ) == [
        "AS14c20S27106M518x529S14c20481x471S27106503x489-C",
        "AS18701S1870aS2e734S20500M518x533S1870a489x515S18701482x490S20500508x496S2e734500x468",
        "S38800464x496-Z2",
    ]


@pytest.mark.parametrize("invalid_input", ["a"])
def test_fsw_parse_text_invalid(invalid_input):
    assert fsw_parse_text(invalid_input) == []


# ------------------------------------------------------------------ #
# FSW Compose Tests
# ------------------------------------------------------------------ #


def test_fsw_compose_symbol_basic():
    assert fsw_compose_symbol({"symbol": "S10000"}) == "S10000"


def test_fsw_compose_symbol_with_coord():
    assert (
        fsw_compose_symbol({"symbol": "S10000", "coord": [500, 500]}) == "S10000500x500"
    )


def test_fsw_compose_symbol_with_style():
    assert fsw_compose_symbol({"symbol": "S10000", "style": "-C"}) == "S10000-C"


def test_fsw_compose_symbol_full():
    assert (
        fsw_compose_symbol({"symbol": "S10000", "coord": [480, 480], "style": "-C"})
        == "S10000480x480-C"
    )


@pytest.mark.parametrize(
    "invalid_input", [{}, {"coord": [500, 500]}, {"symbol": "invalid"}]
)
def test_fsw_compose_symbol_invalid(invalid_input):
    assert fsw_compose_symbol(invalid_input) is None


def test_fsw_compose_sign_empty_signbox():
    assert fsw_compose_sign({"box": "M", "max": [500, 500]}) == "M500x500"


def test_fsw_compose_sign_plain_signbox():
    assert (
        fsw_compose_sign(
            {
                "box": "M",
                "max": [525, 535],
                "spatials": [
                    {"symbol": "S2e748", "coord": [483, 510]},
                    {"symbol": "S10011", "coord": [501, 466]},
                    {"symbol": "S2e704", "coord": [510, 500]},
                    {"symbol": "S10019", "coord": [476, 475]},
                ],
            }
        )
        == "M525x535S2e748483x510S10011501x466S2e704510x500S10019476x475"
    )


def test_fsw_compose_sign_prefixed_signbox():
    assert (
        fsw_compose_sign(
            {
                "sequence": ["S10011", "S10019", "S2e704", "S2e748"],
                "box": "M",
                "max": [525, 535],
                "spatials": [
                    {"symbol": "S2e748", "coord": [483, 510]},
                    {"symbol": "S10011", "coord": [501, 466]},
                    {"symbol": "S2e704", "coord": [510, 500]},
                    {"symbol": "S10019", "coord": [476, 475]},
                ],
            }
        )
        == "AS10011S10019S2e704S2e748M525x535S2e748483x510S10011501x466S2e704510x500S10019476x475"
    )


def test_fsw_compose_sign_prefixed_with_null():
    assert (
        fsw_compose_sign(
            {
                "sequence": ["S10011", "S00000", "S2e704", "S2e748"],
                "box": "M",
                "max": [525, 535],
                "spatials": [
                    {"symbol": "S2e748", "coord": [483, 510]},
                    {"symbol": "S10011", "coord": [501, 466]},
                    {"symbol": "S2e704", "coord": [510, 500]},
                    {"symbol": "S10019", "coord": [476, 475]},
                ],
            }
        )
        == "AS10011S00000S2e704S2e748M525x535S2e748483x510S10011501x466S2e704510x500S10019476x475"
    )


def test_fsw_compose_sign_with_style():
    assert (
        fsw_compose_sign(
            {
                "sequence": ["S10011", "S10019", "S2e704", "S2e748"],
                "box": "M",
                "max": [525, 535],
                "spatials": [
                    {"symbol": "S2e748", "coord": [483, 510]},
                    {"symbol": "S10011", "coord": [501, 466]},
                    {"symbol": "S2e704", "coord": [510, 500]},
                    {"symbol": "S10019", "coord": [476, 475]},
                ],
                "style": "-C",
            }
        )
        == "AS10011S10019S2e704S2e748M525x535S2e748483x510S10011501x466S2e704510x500S10019476x475-C"
    )


# ------------------------------------------------------------------ #
# FSW info
# ------------------------------------------------------------------ #
def test_fsw_info_sign():
    assert fsw_info("AS14c20S27106M518x529S14c20481x471S27106503x489") == {
        "minX": 481,
        "minY": 471,
        "width": 37,
        "height": 58,
        "zoom": 1,
        "padding": 0,
        "segment": "sign",
        "lane": 0,
    }

    assert fsw_info("AS14c20S27106L518x529S14c20481x471S27106503x489-Z2") == {
        "minX": 481,
        "minY": 471,
        "width": 37,
        "height": 58,
        "zoom": 2,
        "padding": 0,
        "segment": "sign",
        "lane": -1,
    }

    assert fsw_info("AS14c20S27106R518x529S14c20481x471S27106503x489-P10Z0.2") == {
        "minX": 481,
        "minY": 471,
        "width": 37,
        "height": 58,
        "zoom": 0.2,
        "padding": 10,
        "segment": "sign",
        "lane": 1,
    }


def test_fsw_info_punctuation_symbol():
    assert fsw_info("S38800464x496") == {
        "minX": 464,
        "minY": 496,
        "width": 72,
        "height": 8,
        "zoom": 1,
        "padding": 0,
        "segment": "symbol",
        "lane": 0,
    }


def test_fsw_info_styled_symbol():
    assert fsw_info("S38800464x496-P10Z2.2") == {
        "minX": 464,
        "minY": 496,
        "width": 72,
        "height": 8,
        "zoom": 2.2,
        "padding": 10,
        "segment": "symbol",
        "lane": 0,
    }


def test_fsw_info_bad_input():
    assert fsw_info("") == {
        "minX": 490,
        "minY": 490,
        "width": 20,
        "height": 20,
        "zoom": 1,
        "padding": 0,
        "segment": "none",
        "lane": 0,
    }
    assert fsw_info("invalid") == {
        "minX": 490,
        "minY": 490,
        "width": 20,
        "height": 20,
        "zoom": 1,
        "padding": 0,
        "segment": "none",
        "lane": 0,
    }


# ------------------------------------------------------------------ #
# FSW Columns
# ------------------------------------------------------------------ #
def test_fsw_column_defaults_merge_empty():
    assert fsw_column_defaults_merge() == {
        "height": 500,
        "width": 150,
        "offset": 50,
        "pad": 20,
        "margin": 5,
        "dynamic": False,
        "punctuation": {
            "pad": 30,
            "pull": True,
            "spacing": True,
        },
        "style": {
            "detail": ["black", "white"],
            "zoom": 1,
        },
    }


def test_fsw_column_defaults_merge_top_level():
    assert fsw_column_defaults_merge({"width": 200}) == {
        "height": 500,
        "width": 200,
        "offset": 50,
        "pad": 20,
        "margin": 5,
        "dynamic": False,
        "punctuation": {
            "pad": 30,
            "pull": True,
            "spacing": True,
        },
        "style": {
            "detail": ["black", "white"],
            "zoom": 1,
        },
    }


def test_fsw_column_defaults_merge_deep_level():
    assert fsw_column_defaults_merge({"punctuation": {"pad": 20}, "width": 200}) == {
        "height": 500,
        "width": 200,
        "offset": 50,
        "pad": 20,
        "margin": 5,
        "dynamic": False,
        "punctuation": {
            "pad": 20,
            "pull": True,
            "spacing": True,
        },
        "style": {
            "detail": ["black", "white"],
            "zoom": 1,
        },
    }
    assert fsw_column_defaults_merge(
        {"style": {"background": "555"}, "width": 200}
    ) == {
        "height": 500,
        "width": 200,
        "offset": 50,
        "pad": 20,
        "margin": 5,
        "dynamic": False,
        "punctuation": {
            "pad": 30,
            "pull": True,
            "spacing": True,
        },
        "style": {
            "detail": ["black", "white"],
            "zoom": 1,
            "background": "555",
        },
    }


def test_fsw_columns_sample():
    hello_world = (
        "AS14c20S27106M518x529S14c20481x471S27106503x489 "
        "AS18701S1870aS2e734S20500M518x533S1870a489x515S18701482x490S20500508x496S2e734500x468 "
        "S38800464x496"
    )
    assert fsw_columns(hello_world) == {
        "options": {
            "height": 500,
            "width": 150,
            "offset": 50,
            "pad": 20,
            "margin": 5,
            "dynamic": False,
            "punctuation": {
                "pad": 30,
                "pull": True,
                "spacing": True,
            },
            "style": {
                "detail": ["black", "white"],
                "zoom": 1,
            },
        },
        "widths": [150],
        "columns": [
            [
                {
                    "x": 56,
                    "y": 20,
                    "minX": 481,
                    "minY": 471,
                    "width": 37,
                    "height": 58,
                    "lane": 0,
                    "padding": 0,
                    "segment": "sign",
                    "text": "AS14c20S27106M518x529S14c20481x471S27106503x489",
                    "zoom": 1,
                },
                {
                    "x": 57,
                    "y": 118,
                    "minX": 482,
                    "minY": 468,
                    "width": 36,
                    "height": 65,
                    "lane": 0,
                    "padding": 0,
                    "segment": "sign",
                    "text": "AS18701S1870aS2e734S20500M518x533S1870a489x515S18701482x490S20500508x496S2e734500x468",
                    "zoom": 1,
                },
                {
                    "x": 39,
                    "y": 203,
                    "minX": 464,
                    "minY": 496,
                    "width": 72,
                    "height": 8,
                    "lane": 0,
                    "padding": 0,
                    "segment": "symbol",
                    "text": "S38800464x496",
                    "zoom": 1,
                },
            ],
        ],
    }


def test_fsw_columns_zoomx():
    zoomx = (
        "AS14c20S27106M518x529S14c20481x471S27106503x489-Zx "
        "AS18701S1870aS2e734S20500M518x533S1870a489x515S18701482x490S20500508x496S2e734500x468 "
        "S38800464x496"
    )
    assert fsw_columns(zoomx) == {
        "options": {
            "height": 500,
            "width": 150,
            "offset": 50,
            "pad": 20,
            "margin": 5,
            "dynamic": False,
            "punctuation": {
                "pad": 30,
                "pull": True,
                "spacing": True,
            },
            "style": {
                "detail": ["black", "white"],
                "zoom": 1,
            },
        },
        "widths": [150],
        "columns": [
            [
                {
                    "x": 56,
                    "y": 20,
                    "minX": 481,
                    "minY": 471,
                    "width": 37,
                    "height": 58,
                    "lane": 0,
                    "padding": 0,
                    "segment": "sign",
                    "text": "AS14c20S27106M518x529S14c20481x471S27106503x489-Zx",
                    "zoom": 1,
                },
                {
                    "x": 57,
                    "y": 118,
                    "minX": 482,
                    "minY": 468,
                    "width": 36,
                    "height": 65,
                    "lane": 0,
                    "padding": 0,
                    "segment": "sign",
                    "text": "AS18701S1870aS2e734S20500M518x533S1870a489x515S18701482x490S20500508x496S2e734500x468",
                    "zoom": 1,
                },
                {
                    "x": 39,
                    "y": 203,
                    "minX": 464,
                    "minY": 496,
                    "width": 72,
                    "height": 8,
                    "lane": 0,
                    "padding": 0,
                    "segment": "symbol",
                    "text": "S38800464x496",
                    "zoom": 1,
                },
            ],
        ],
    }


def test_fsw_columns_bad_input():
    assert fsw_columns(5) == {}
    assert fsw_columns(["what"]) == {}


# ------------------------------------------------------------------ #
# FSW Tokenizer
# ------------------------------------------------------------------ #
def test_fsw_tokenize_single_sign():
    fsw = "M523x556S1f720487x492S1f72f487x492"
    tokens = fsw_tokenize(fsw)
    assert tokens == [
        "M",
        "p523",
        "p556",
        "S1f7",
        "c2",
        "r0",
        "p487",
        "p492",
        "S1f7",
        "c2",
        "rf",
        "p487",
        "p492",
        "[SEP]",
    ]


def test_fsw_tokenize_no_box():
    fsw = "S38800464x496"
    tokens = fsw_tokenize(fsw)
    assert tokens == ["M", "p536", "p504", "S388", "c0", "r0", "p464", "p496", "[SEP]"]


def test_fsw_tokenize_multiple_signs():
    fsw = "M523x556S1f720487x492 M524x556S1f210488x493"
    tokens = fsw_tokenize(fsw)
    assert tokens == [
        "M",
        "p523",
        "p556",
        "S1f7",
        "c2",
        "r0",
        "p487",
        "p492",
        "[SEP]",
        "M",
        "p524",
        "p556",
        "S1f2",
        "c1",
        "r0",
        "p488",
        "p493",
        "[SEP]",
    ]


def test_fsw_tokenize_with_a():
    fsw = "AS1f720M523x556S1f720487x492"
    tokens = fsw_tokenize(fsw)
    assert tokens == [
        "A",
        "S1f7",
        "c2",
        "r0",
        "M",
        "p523",
        "p556",
        "S1f7",
        "c2",
        "r0",
        "p487",
        "p492",
        "[SEP]",
    ]


def test_fsw_detokenize_single_symbol():
    tokens = ["S388", "c0", "r0", "p464", "p496"]
    assert fsw_detokenize(tokens) == "S38800464x496"


def test_fsw_detokenize_multiple_symbols_with_m_prefix():
    tokens = [
        "M",
        "p523",
        "p556",
        "S1f7",
        "c2",
        "r0",
        "p487",
        "p492",
        "S1f7",
        "c2",
        "r0",
        "p487",
        "p492",
    ]
    assert fsw_detokenize(tokens) == "M523x556S1f720487x492S1f720487x492"


def test_fsw_detokenize_multiple_symbols_with_a_prefix():
    tokens = [
        "A",
        "S1f7",
        "c2",
        "r0",
        "M",
        "p523",
        "p556",
        "S1f7",
        "c2",
        "r0",
        "p487",
        "p492",
        "S1f7",
        "c2",
        "r0",
        "p487",
        "p492",
    ]
    assert fsw_detokenize(tokens) == "AS1f720M523x556S1f720487x492S1f720487x492"


def test_fsw_detokenize_multiple_signs():
    tokens = [
        "M",
        "p523",
        "p556",
        "S1f7",
        "c2",
        "r0",
        "p487",
        "p492",
        "M",
        "p524",
        "p556",
        "S1f2",
        "c1",
        "r0",
        "p488",
        "p493",
    ]
    assert fsw_detokenize(tokens) == "M523x556S1f720487x492 M524x556S1f210488x493"


def test_fsw_detokenize_empty():
    assert fsw_detokenize([]) == ""


def test_fsw_detokenize_all_box_types():
    box_types = ["B", "L", "M", "R"]
    for box in box_types:
        tokens = [box, "p523", "p556", "S1f7", "c2", "r0", "p487", "p492"]
        assert fsw_detokenize(tokens) == f"{box}523x556S1f720487x492"


def test_fsw_tokenizer_single_sign():
    t = FSWTokenizer()
    fsw = "M523x556S1f720487x492S1f720487x492"
    tokens = t.encode(fsw)
    expected = [
        t.s2i["M"],
        t.s2i["p523"],
        t.s2i["p556"],
        t.s2i["S1f7"],
        t.s2i["c2"],
        t.s2i["r0"],
        t.s2i["p487"],
        t.s2i["p492"],
        t.s2i["S1f7"],
        t.s2i["c2"],
        t.s2i["r0"],
        t.s2i["p487"],
        t.s2i["p492"],
        t.s2i["[SEP]"],
    ]
    assert tokens == expected


def test_fsw_tokenizer_no_box():
    t = FSWTokenizer()
    fsw = "S38800464x496"
    tokens = t.encode(fsw)
    expected = [
        t.s2i[tok]
        for tok in ["M", "p536", "p504", "S388", "c0", "r0", "p464", "p496", "[SEP]"]
    ]
    assert tokens == expected


def test_fsw_tokenizer_multiple_signs():
    t = FSWTokenizer()
    fsw = "M523x556S1f720487x492 M524x556S1f210488x493"
    tokens = t.encode(fsw)
    expected = [
        t.s2i[tok]
        for tok in [
            "M",
            "p523",
            "p556",
            "S1f7",
            "c2",
            "r0",
            "p487",
            "p492",
            "[SEP]",
            "M",
            "p524",
            "p556",
            "S1f2",
            "c1",
            "r0",
            "p488",
            "p493",
            "[SEP]",
        ]
    ]
    assert tokens == expected


def test_fsw_tokenizer_with_a():
    t = FSWTokenizer()
    fsw = "AS1f720M523x556S1f720487x492"
    tokens = t.encode(fsw)
    expected = [
        t.s2i[tok]
        for tok in [
            "A",
            "S1f7",
            "c2",
            "r0",
            "M",
            "p523",
            "p556",
            "S1f7",
            "c2",
            "r0",
            "p487",
            "p492",
            "[SEP]",
        ]
    ]
    assert tokens == expected


def test_fsw_tokenizer_decode_single_sign():
    t = FSWTokenizer()
    tokens = [
        t.s2i[tok]
        for tok in [
            "M",
            "p251",
            "p456",
            "S1f7",
            "c2",
            "r0",
            "p487",
            "p492",
            "S1f7",
            "c2",
            "r0",
            "p487",
            "p492",
            "[SEP]",
        ]
    ]
    fsw = t.decode(tokens)
    assert fsw == "M251x456S1f720487x492S1f720487x492"


def test_fsw_tokenizer_decode_multiple_signs():
    t = FSWTokenizer()
    tokens = [
        t.s2i[tok]
        for tok in [
            "M",
            "p251",
            "p456",
            "S1f7",
            "c2",
            "r0",
            "p487",
            "p492",
            "[SEP]",
            "M",
            "p524",
            "p556",
            "S1f2",
            "c1",
            "r0",
            "p488",
            "p493",
            "[SEP]",
        ]
    ]
    fsw = t.decode(tokens)
    assert fsw == "M251x456S1f720487x492 M524x556S1f210488x493"


def test_fsw_tokenizer_empty_special_tokens():
    t = FSWTokenizer([])
    assert t.s2i["A"] == 0


def test_fsw_tokenizer_non_sequential_special_tokens():
    special_tokens = [
        {"index": 0, "name": "UNK", "value": "[UNK]"},
        {"index": 5, "name": "PAD", "value": "[PAD]"},
        {"index": 10, "name": "CLS", "value": "[CLS]"},
        {"index": 15, "name": "SEP", "value": "[SEP]"},
    ]
    t = FSWTokenizer(special_tokens)
    assert t.s2i["A"] == 16


def test_fsw_tokenizer_custom_starting_index():
    special_tokens = [
        {"index": 0, "name": "UNK", "value": "[UNK]"},
        {"index": 5, "name": "PAD", "value": "[PAD]"},
        {"index": 10, "name": "CLS", "value": "[CLS]"},
        {"index": 15, "name": "SEP", "value": "[SEP]"},
    ]
    t = FSWTokenizer(special_tokens, 100)
    assert t.s2i["A"] == 100


def test_fsw_tokenizer_empty_special_with_custom_start():
    t = FSWTokenizer([], 10)
    assert t.s2i["A"] == 10
