"""
pytest suite for the structure functions.
"""

from __future__ import annotations

import pytest

# ------------------------------------------------------------------ #
# Import the public API
# ------------------------------------------------------------------ #
from sutton_signwriting_core import (
    swu_is_type,
    swu_colorize,
    swu_parse_symbol,
    swu_parse_sign,
    swu_parse_text,
    swu_compose_symbol,
    swu_compose_sign,
    swu_info,
    swu_column_defaults_merge,
    swu_columns,
)


# ------------------------------------------------------------------ #
# Structure classification
# ------------------------------------------------------------------ #
def test_swu_is_type():
    assert swu_is_type("\U00040001", "writing") is True  # index symbol
    assert swu_is_type("\U00040012", "hand") is True  # S10011
    assert swu_is_type("\U0001D816", "hand") is False  # a number char
    assert swu_is_type("\U00040000", "invalid") is False


# ------------------------------------------------------------------ #
# Colorize
# ------------------------------------------------------------------ #
def test_swu_colorize_right_color():
    assert swu_colorize("񀀁") == "#0000CC"
    assert swu_colorize("񆉁") == "#CC0000"
    assert swu_colorize("񋲡") == "#FF0099"
    assert swu_colorize("񎋡") == "#006600"
    assert swu_colorize("񎣡") == "#000000"
    assert swu_colorize("񎾡") == "#884411"
    assert swu_colorize("񏐡") == "#FF9900"
    assert swu_colorize("\U00040000") == "#000000"


def test_swu_colorize_bad_input():
    assert swu_colorize(5) == "#000000"
    assert swu_colorize(["what"]) == "#000000"


# ------------------------------------------------------------------ #
# SWU Parsing Tests
# ------------------------------------------------------------------ #


def test_swu_parse_symbol_basic():
    assert swu_parse_symbol("񀀁") == {"symbol": "񀀁"}


def test_swu_parse_symbol_with_coord():
    assert swu_parse_symbol("񀀁𝤆𝤆") == {"symbol": "񀀁", "coord": [500, 500]}


def test_swu_parse_symbol_with_style():
    assert swu_parse_symbol("񀀁-C") == {"symbol": "񀀁", "style": "-C"}


@pytest.mark.parametrize("invalid_input", ["a"])
def test_swu_parse_symbol_invalid(invalid_input):
    assert swu_parse_symbol(invalid_input) == {}


def test_swu_parse_sign_empty_signbox():
    assert swu_parse_sign("𝠃𝤆𝤆") == {"box": "𝠃", "max": [500, 500]}


def test_swu_parse_sign_plain_signbox():
    assert swu_parse_sign("𝠃𝤟𝤩񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭") == {
        "box": "𝠃",
        "max": [525, 535],
        "spatials": [
            {"symbol": "񋛩", "coord": [483, 510]},
            {"symbol": "񀀒", "coord": [501, 466]},
            {"symbol": "񋚥", "coord": [510, 500]},
            {"symbol": "񀀚", "coord": [476, 475]},
        ],
    }


def test_swu_parse_sign_prefixed_signbox():
    assert swu_parse_sign("𝠀񀀒񀀚񋚥񋛩𝠃𝤟𝤩񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭") == {
        "sequence": ["񀀒", "񀀚", "񋚥", "񋛩"],
        "box": "𝠃",
        "max": [525, 535],
        "spatials": [
            {"symbol": "񋛩", "coord": [483, 510]},
            {"symbol": "񀀒", "coord": [501, 466]},
            {"symbol": "񋚥", "coord": [510, 500]},
            {"symbol": "񀀚", "coord": [476, 475]},
        ],
    }


def test_swu_parse_sign_prefixed_with_style():
    assert swu_parse_sign("𝠀񀀒񀀚񋚥񋛩𝠃𝤟𝤩񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭-C") == {
        "sequence": ["񀀒", "񀀚", "񋚥", "񋛩"],
        "box": "𝠃",
        "max": [525, 535],
        "spatials": [
            {"symbol": "񋛩", "coord": [483, 510]},
            {"symbol": "񀀒", "coord": [501, 466]},
            {"symbol": "񋚥", "coord": [510, 500]},
            {"symbol": "񀀚", "coord": [476, 475]},
        ],
        "style": "-C",
    }


@pytest.mark.parametrize("invalid_input", ["a"])
def test_swu_parse_sign_invalid(invalid_input):
    assert swu_parse_sign(invalid_input) == {}


def test_swu_parse_text_basic():
    assert swu_parse_text("𝠀񁲡񈩧𝠃𝤘𝤣񁲡𝣳𝣩񈩧𝤉𝣻 𝠀񃊢񃊫񋛕񆇡𝠃𝤘𝤧񃊫𝣻𝤕񃊢𝣴𝣼񆇡𝤎𝤂񋛕𝤆𝣦 񏌁𝣢𝤂") == [
        "𝠀񁲡񈩧𝠃𝤘𝤣񁲡𝣳𝣩񈩧𝤉𝣻",
        "𝠀񃊢񃊫񋛕񆇡𝠃𝤘𝤧񃊫𝣻𝤕񃊢𝣴𝣼񆇡𝤎𝤂񋛕𝤆𝣦",
        "񏌁𝣢𝤂",
    ]


def test_swu_parse_text_with_style():
    assert swu_parse_text("𝠀񁲡񈩧𝠃𝤘𝤣񁲡𝣳𝣩񈩧𝤉𝣻-C 𝠀񃊢񃊫񋛕񆇡𝠃𝤘𝤧񃊫𝣻𝤕񃊢𝣴𝣼񆇡𝤎𝤂񋛕𝤆𝣦 񏌁𝣢𝤂-Z2") == [
        "𝠀񁲡񈩧𝠃𝤘𝤣񁲡𝣳𝣩񈩧𝤉𝣻-C",
        "𝠀񃊢񃊫񋛕񆇡𝠃𝤘𝤧񃊫𝣻𝤕񃊢𝣴𝣼񆇡𝤎𝤂񋛕𝤆𝣦",
        "񏌁𝣢𝤂-Z2",
    ]


@pytest.mark.parametrize("invalid_input", ["a"])
def test_swu_parse_text_invalid(invalid_input):
    assert swu_parse_text(invalid_input) == []


# ------------------------------------------------------------------ #
# SWU Compose Tests (inverse of swu/swu-parse.test.js)
# ------------------------------------------------------------------ #


def test_swu_compose_symbol_basic():
    assert swu_compose_symbol({"symbol": "񀀁"}) == "񀀁"


def test_swu_compose_symbol_with_coord():
    assert swu_compose_symbol({"symbol": "񀀁", "coord": [500, 500]}) == "񀀁𝤆𝤆"


def test_swu_compose_symbol_with_style():
    assert swu_compose_symbol({"symbol": "񀀁", "style": "-C"}) == "񀀁-C"


def test_swu_compose_symbol_full():
    assert (
        swu_compose_symbol({"symbol": "񀀁", "coord": [500, 500], "style": "-C"})
        == "񀀁𝤆𝤆-C"
    )


@pytest.mark.parametrize(
    "invalid_input",
    [{}, {"coord": [500, 500]}, {"symbol": "A"}, {"symbol": "x", "coord": [9999, 500]}],
)
def test_swu_compose_symbol_invalid(invalid_input):
    assert swu_compose_symbol(invalid_input) is None


def test_swu_compose_sign_empty_signbox():
    assert swu_compose_sign({"box": "𝠃", "max": [500, 500]}) == "𝠃𝤆𝤆"


def test_swu_compose_sign_plain_signbox():
    assert (
        swu_compose_sign(
            {
                "box": "𝠃",
                "max": [525, 535],
                "spatials": [
                    {"symbol": "񋛩", "coord": [483, 510]},
                    {"symbol": "񀀒", "coord": [501, 466]},
                    {"symbol": "񋚥", "coord": [510, 500]},
                    {"symbol": "񀀚", "coord": [476, 475]},
                ],
            }
        )
        == "𝠃𝤟𝤩񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭"
    )


def test_swu_compose_sign_prefixed_signbox():
    assert (
        swu_compose_sign(
            {
                "sequence": ["񀀒", "񀀚", "񋚥", "񋛩"],
                "box": "𝠃",
                "max": [525, 535],
                "spatials": [
                    {"symbol": "񋛩", "coord": [483, 510]},
                    {"symbol": "񀀒", "coord": [501, 466]},
                    {"symbol": "񋚥", "coord": [510, 500]},
                    {"symbol": "񀀚", "coord": [476, 475]},
                ],
            }
        )
        == "𝠀񀀒񀀚񋚥񋛩𝠃𝤟𝤩񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭"
    )


def test_swu_compose_sign_with_style():
    assert (
        swu_compose_sign(
            {
                "sequence": ["񀀒", "񀀚", "񋚥", "񋛩"],
                "box": "𝠃",
                "max": [525, 535],
                "spatials": [
                    {"symbol": "񋛩", "coord": [483, 510]},
                    {"symbol": "񀀒", "coord": [501, 466]},
                    {"symbol": "񋚥", "coord": [510, 500]},
                    {"symbol": "񀀚", "coord": [476, 475]},
                ],
                "style": "-C",
            }
        )
        == "𝠀񀀒񀀚񋚥񋛩𝠃𝤟𝤩񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭-C"
    )


# ------------------------------------------------------------------ #
# SWU info
# ------------------------------------------------------------------ #
def test_swu_info_sign():
    assert swu_info("𝠀񁲡񈩧𝠃𝤘𝤣񁲡𝣳𝣩񈩧𝤉𝣻") == {
        "minX": 481,
        "minY": 471,
        "width": 37,
        "height": 58,
        "zoom": 1,
        "padding": 0,
        "segment": "sign",
        "lane": 0,
    }

    assert swu_info("𝠀񁲡񈩧𝠂𝤘𝤣񁲡𝣳𝣩񈩧𝤉𝣻-Z2") == {
        "minX": 481,
        "minY": 471,
        "width": 37,
        "height": 58,
        "zoom": 2,
        "padding": 0,
        "segment": "sign",
        "lane": -1,
    }

    assert swu_info("𝠀񁲡񈩧𝠄𝤘𝤣񁲡𝣳𝣩񈩧𝤉𝣻-P10Z0.2") == {
        "minX": 481,
        "minY": 471,
        "width": 37,
        "height": 58,
        "zoom": 0.2,
        "padding": 10,
        "segment": "sign",
        "lane": 1,
    }


def test_swu_info_punctuation_symbol():
    assert swu_info("񏌁𝣢𝤂") == {
        "minX": 464,
        "minY": 496,
        "width": 72,
        "height": 8,
        "zoom": 1,
        "padding": 0,
        "segment": "symbol",
        "lane": 0,
    }


def test_swu_info_styled_symbol():
    assert swu_info("񏌁𝣢𝤂-P10Z2.2") == {
        "minX": 464,
        "minY": 496,
        "width": 72,
        "height": 8,
        "zoom": 2.2,
        "padding": 10,
        "segment": "symbol",
        "lane": 0,
    }


def test_swu_info_bad_input():
    assert swu_info("") == {
        "minX": 490,
        "minY": 490,
        "width": 20,
        "height": 20,
        "zoom": 1,
        "padding": 0,
        "segment": "none",
        "lane": 0,
    }
    assert swu_info("invalid") == {
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
# SWU Columns
# ------------------------------------------------------------------ #
def test_swu_column_defaults_merge_empty():
    assert swu_column_defaults_merge() == {
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


def test_swu_column_defaults_merge_top_level():
    assert swu_column_defaults_merge({"width": 200}) == {
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


def test_swu_column_defaults_merge_deep_level():
    assert swu_column_defaults_merge({"punctuation": {"pad": 20}, "width": 200}) == {
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
    assert swu_column_defaults_merge(
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


def test_swu_columns_sample():
    hello_world = "𝠀񁲡񈩧𝠃𝤘𝤣񁲡𝣳𝣩񈩧𝤉𝣻 𝠀񃊢񃊫񋛕񆇡𝠃𝤘𝤧񃊫𝣻𝤕񃊢𝣴𝣼񆇡𝤎𝤂񋛕𝤆𝣦 񏌁𝣢𝤂"
    assert swu_columns(hello_world) == {
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
                    "text": "𝠀񁲡񈩧𝠃𝤘𝤣񁲡𝣳𝣩񈩧𝤉𝣻",
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
                    "text": "𝠀񃊢񃊫񋛕񆇡𝠃𝤘𝤧񃊫𝣻𝤕񃊢𝣴𝣼񆇡𝤎𝤂񋛕𝤆𝣦",
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
                    "text": "񏌁𝣢𝤂",
                    "zoom": 1,
                },
            ],
        ],
    }


def test_swu_columns_bad_input():
    assert swu_columns(5) == {}
    assert swu_columns(["what"]) == {}
