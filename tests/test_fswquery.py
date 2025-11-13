"""
pytest suite for the parse functions.
"""

from __future__ import annotations

import pytest

import re

import random

# ------------------------------------------------------------------ #
# Import the public API
# ------------------------------------------------------------------ #
from sutton_signwriting_core import (
    fswquery_parse,
    fswquery_compose,
    fsw_to_query,
    fswquery_range,
    fswquery_regex,
    fswquery_results,
    fswquery_lines,
)


# ------------------------------------------------------------------ #
# FSW Query Parsing Tests
# ------------------------------------------------------------------ #


def test_fswquery_parse_generic():
    assert fswquery_parse("Q") == {"query": True}
    assert fswquery_parse("Q-") == {"query": True, "style": True}


def test_fswquery_parse_prefix_basic():
    assert fswquery_parse("QT") == {"query": True, "prefix": {"required": True}}
    assert fswquery_parse("QT-") == {
        "query": True,
        "prefix": {"required": True},
        "style": True,
    }


def test_fswquery_parse_prefix_parts():
    assert fswquery_parse("QAS10000R100t204S20500T") == {
        "query": True,
        "prefix": {"required": True, "parts": ["S10000", ["100", "204"], "S20500"]},
    }


def test_fswquery_parse_prefix_with_or():
    assert fswquery_parse("QAS10000R100t204oS20500T") == {
        "query": True,
        "prefix": {
            "required": True,
            "parts": ["S10000", ["or_list", ["100", "204"], "S20500"]],
        },
    }


def test_fswquery_parse_signbox_basic():
    assert fswquery_parse("QS10000") == {
        "query": True,
        "signbox": [{"symbol": "S10000"}],
    }


def test_fswquery_parse_signbox_with_coord():
    assert fswquery_parse("QS100uu500x500") == {
        "query": True,
        "signbox": [{"symbol": "S100uu", "coord": [500, 500]}],
    }


def test_fswquery_parse_signbox_range():
    assert fswquery_parse("QR100t105") == {
        "query": True,
        "signbox": [{"range": ["100", "105"]}],
    }


def test_fswquery_parse_signbox_range_with_coord():
    assert fswquery_parse("QR100t105500x500") == {
        "query": True,
        "signbox": [{"range": ["100", "105"], "coord": [500, 500]}],
    }


def test_fswquery_parse_signbox_mixed():
    assert fswquery_parse("QS1000uR100t105500x500") == {
        "query": True,
        "signbox": [
            {"symbol": "S1000u"},
            {"range": ["100", "105"], "coord": [500, 500]},
        ],
    }


def test_fswquery_parse_signbox_with_or():
    assert fswquery_parse("QS1000uoR100t105500x500") == {
        "query": True,
        "signbox": [{"or_list": ["S1000u", ["100", "105"]], "coord": [500, 500]}],
    }


@pytest.mark.parametrize("invalid_input", ["a"])
def test_fswquery_parse_invalid(invalid_input):
    assert fswquery_parse(invalid_input) == {"query": False}


# ------------------------------------------------------------------ #
# FSW Query Compose Tests
# ------------------------------------------------------------------ #


def test_fswquery_compose_generic():
    assert fswquery_compose({"query": True}) == "Q"
    assert fswquery_compose({"query": True, "style": True}) == "Q-"


def test_fswquery_compose_prefix_basic():
    assert fswquery_compose({"query": True, "prefix": {"required": True}}) == "QT"
    assert (
        fswquery_compose({"query": True, "prefix": {"required": True}, "style": True})
        == "QT-"
    )


def test_fswquery_compose_prefix_parts():
    assert (
        fswquery_compose(
            {
                "query": True,
                "prefix": {
                    "required": True,
                    "parts": ["S10000", ["100", "204"], "S20500"],
                },
            }
        )
        == "QAS10000R100t204S20500T"
    )


def test_fswquery_compose_prefix_with_or():
    assert (
        fswquery_compose(
            {
                "query": True,
                "prefix": {
                    "required": True,
                    "parts": ["S10000", ["or_list", ["100", "204"], "S20500"]],
                },
            }
        )
        == "QAS10000R100t204oS20500T"
    )


def test_fswquery_compose_signbox_basic():
    assert (
        fswquery_compose({"query": True, "signbox": [{"symbol": "S10000"}]})
        == "QS10000"
    )


def test_fswquery_compose_signbox_with_coord():
    assert (
        fswquery_compose(
            {"query": True, "signbox": [{"symbol": "S100uu", "coord": [500, 500]}]}
        )
        == "QS100uu500x500"
    )


def test_fswquery_compose_signbox_range():
    assert (
        fswquery_compose({"query": True, "signbox": [{"range": ["100", "105"]}]})
        == "QR100t105"
    )


def test_fswquery_compose_signbox_range_with_coord():
    assert (
        fswquery_compose(
            {"query": True, "signbox": [{"range": ["100", "105"], "coord": [500, 500]}]}
        )
        == "QR100t105500x500"
    )


def test_fswquery_compose_signbox_mixed():
    assert (
        fswquery_compose(
            {
                "query": True,
                "signbox": [
                    {"symbol": "S1000u"},
                    {"range": ["100", "105"], "coord": [500, 500]},
                ],
            }
        )
        == "QS1000uR100t105500x500"
    )


def test_fswquery_compose_signbox_with_or():
    assert (
        fswquery_compose(
            {
                "query": True,
                "signbox": [
                    {"or_list": ["S1000u", ["100", "105"]], "coord": [500, 500]}
                ],
            }
        )
        == "QS1000uoR100t105500x500"
    )


def test_fswquery_compose_full_example():
    assert (
        fswquery_compose(
            {
                "query": True,
                "prefix": {
                    "required": True,
                    "parts": ["S10000", ["100", "204"], "S20500"],
                },
                "signbox": [
                    {"symbol": "S20000"},
                    {"range": ["100", "105"], "coord": [500, 500]},
                ],
                "variance": 5,
                "style": True,
            }
        )
        == "QAS10000R100t204S20500TS20000R100t105500x500V5-"
    )


@pytest.mark.parametrize("invalid_input", [{}, {"query": False}])
def test_fswquery_compose_invalid(invalid_input):
    assert fswquery_compose(invalid_input) is None


# ------------------------------------------------------------------ #
# FSW to Query Tests
# ------------------------------------------------------------------ #


def test_fsw_to_query():
    fsw = "AS10011S10019S2e704S2e748M525x535S2e748483x510S10011501x466S2e704510x500S10019476x475"
    assert (
        fsw_to_query(fsw, "ASL")
        == "QAS10011S10019S2e704S2e748TS2e748483x510S10011501x466S2e704510x500S10019476x475"
    )
    assert fsw_to_query(fsw, "a") == "QAS100uuS100uuS2e7uuS2e7uuT"
    assert (
        fsw_to_query(fsw, "sL")
        == "QS2e7uu483x510S100uu501x466S2e7uu510x500S100uu476x475"
    )


def test_fsw_to_query_bad_input():
    assert fsw_to_query("invalid", "ASL") is None
    assert fsw_to_query("S10000490x490", "ASL") is None


# ------------------------------------------------------------------ #
# FSW Query Range Tests
# ------------------------------------------------------------------ #


def test_fswquery_range_decimal():
    failures = []
    errors = []
    tested_count = 0
    total_count = 0
    exhaustive = False
    sample_rate = 0.05

    for start in range(250, 750):
        for end in range(start, 751):
            total_count += 1
            if not (exhaustive or random.random() < sample_rate):
                continue
            tested_count += 1
            try:
                regex_pattern = fswquery_range(start, end)
                regex = re.compile(regex_pattern)
                test_nums = [
                    start - 1,
                    start,
                    (start + end) // 2,
                    end,
                    end + 1,
                ] + random.sample(range(100, 1000), 10)
                for num in set(test_nums):
                    if num < 100 or num > 999:
                        continue
                    num_str = f"{num:03d}"
                    regex_match = regex.match(num_str) is not None
                    numerical_match = start <= num <= end
                    if regex_match != numerical_match:
                        failures.append(
                            {
                                "start": start,
                                "end": end,
                                "num": num,
                                "regex_match": regex_match,
                                "numerical_match": numerical_match,
                                "pattern": regex_pattern,
                            }
                        )
            except Exception as e:
                errors.append({"start": start, "end": end, "error": str(e)})

    assert (
        len(failures) == 0
    ), f"Found {len(failures)} decimal failures. First: {failures[0] if failures else None}"
    assert (
        len(errors) == 0
    ), f"Found {len(errors)} errors. First: {errors[0] if errors else None}"


def test_fswquery_range_hex():
    def num_to_hex(num: int) -> str:
        return f"{num:03x}"

    failures = []
    errors = []
    tested_count = 0
    total_count = 0
    exhaustive = False
    sample_rate = 0.05

    for start_num in range(0x100, 0x38C):
        start = num_to_hex(start_num)
        for end_num in range(start_num, 0x38C):
            end = num_to_hex(end_num)
            total_count += 1
            if not (exhaustive or random.random() < sample_rate):
                continue
            tested_count += 1
            try:
                regex_pattern = fswquery_range(start, end, True)
                regex = re.compile(regex_pattern)
                test_nums = [
                    start_num - 1,
                    start_num,
                    (start_num + end_num) // 2,
                    end_num,
                    end_num + 1,
                ] + random.sample(range(0x100, 0x1000), 10)
                for num in set(test_nums):
                    if num < 0x100 or num > 0x38B:
                        continue
                    num_str = num_to_hex(num)
                    regex_match = regex.match(num_str) is not None
                    numerical_match = start_num <= num <= end_num
                    if regex_match != numerical_match:
                        failures.append(
                            {
                                "start": start,
                                "end": end,
                                "num": num_str,
                                "regex_match": regex_match,
                                "numerical_match": numerical_match,
                                "pattern": regex_pattern,
                            }
                        )
            except Exception as e:
                errors.append({"start": start, "end": end, "error": str(e)})

    assert (
        len(failures) == 0
    ), f"Found {len(failures)} hex failures. First: {failures[0] if failures else None}"
    assert (
        len(errors) == 0
    ), f"Found {len(errors)} errors. First: {errors[0] if errors else None}"


# ------------------------------------------------------------------ #
# FSW Query Regex Tests
# ------------------------------------------------------------------ #


def test_fswquery_general_query():
    assert fswquery_regex("Q") == [
        "(?:A(?:S00000|S[123][0-9a-f]{2}[0-5][0-9a-f])+)?[BLMR][0-9]{3}x[0-9]{3}(?:S[123][0-9a-f]{2}[0-5][0-9a-f][0-9]{3}x[0-9]{3})*"
    ]


def test_fswquery_complex_query_1():
    assert fswquery_regex("QAS10000R100t204S20500T") == [
        "(?:AS10000S(?:1[0-9a-f][0-9a-f]|20[0-4])[0-5][0-9a-f]S20500(?:S00000|S[123][0-9a-f]{2}[0-5][0-9a-f])*)[BLMR][0-9]{3}x[0-9]{3}(?:S[123][0-9a-f]{2}[0-5][0-9a-f][0-9]{3}x[0-9]{3})*"
    ]


def test_fswquery_complex_query_2():
    assert fswquery_regex("QAS10000R100t204S20500TS20000500x500") == [
        "(?:AS10000S(?:1[0-9a-f][0-9a-f]|20[0-4])[0-5][0-9a-f]S20500(?:S00000|S[123][0-9a-f]{2}[0-5][0-9a-f])*)[BLMR][0-9]{3}x[0-9]{3}(?:S[123][0-9a-f]{2}[0-5][0-9a-f][0-9]{3}x[0-9]{3})*S20000(?:4[8-9][0-9]|5(?:[0-1][0-9]|20))x(?:4[8-9][0-9]|5(?:[0-1][0-9]|20))(?:S[123][0-9a-f]{2}[0-5][0-9a-f][0-9]{3}x[0-9]{3})*"
    ]


def test_fswquery_query_with_styling():
    assert fswquery_regex("QS20000R100t105500x500-") == [
        "(?:A(?:S00000|S[123][0-9a-f]{2}[0-5][0-9a-f])+)?[BLMR][0-9]{3}x[0-9]{3}(?:S[123][0-9a-f]{2}[0-5][0-9a-f][0-9]{3}x[0-9]{3})*S20000[0-9]{3}x[0-9]{3}(?:S[123][0-9a-f]{2}[0-5][0-9a-f][0-9]{3}x[0-9]{3})*(?:-(?:C)?(?:P[0-9]{2})?(?:G_(?:(?:[0-9a-fA-F]{3}){1,2}|[a-zA-Z]+)_)?(?:D_(?:(?:[0-9a-fA-F]{3}){1,2}|[a-zA-Z]+)(?:,(?:(?:[0-9a-fA-F]{3}){1,2}|[a-zA-Z]+))?_)?(?:Z(?:[0-9]+(?:\\.[0-9]+)?|x))?(?:-(?:(?:D[0-9]{2}_(?:(?:[0-9a-fA-F]{3}){1,2}|[a-zA-Z]+)(?:,(?:(?:[0-9a-fA-F]{3}){1,2}|[a-zA-Z]+))?_)*))?(?:-(?:-?[_a-zA-Z][_a-zA-Z0-9-]{0,100}(?: -?[_a-zA-Z][_a-zA-Z0-9-]{0,100})*)?!(?:(?:[a-zA-Z][_a-zA-Z0-9-]{0,100})!)?)?)?",
        "(?:A(?:S00000|S[123][0-9a-f]{2}[0-5][0-9a-f])+)?[BLMR][0-9]{3}x[0-9]{3}(?:S[123][0-9a-f]{2}[0-5][0-9a-f][0-9]{3}x[0-9]{3})*S10[0-5][0-5][0-9a-f](?:4[8-9][0-9]|5(?:[0-1][0-9]|20))x(?:4[8-9][0-9]|5(?:[0-1][0-9]|20))(?:S[123][0-9a-f]{2}[0-5][0-9a-f][0-9]{3}x[0-9]{3})*(?:-(?:C)?(?:P[0-9]{2})?(?:G_(?:(?:[0-9a-fA-F]{3}){1,2}|[a-zA-Z]+)_)?(?:D_(?:(?:[0-9a-fA-F]{3}){1,2}|[a-zA-Z]+)(?:,(?:(?:[0-9a-fA-F]{3}){1,2}|[a-zA-Z]+))?_)?(?:Z(?:[0-9]+(?:\\.[0-9]+)?|x))?(?:-(?:(?:D[0-9]{2}_(?:(?:[0-9a-fA-F]{3}){1,2}|[a-zA-Z]+)(?:,(?:(?:[0-9a-fA-F]{3}){1,2}|[a-zA-Z]+))?_)*))?(?:-(?:-?[_a-zA-Z][_a-zA-Z0-9-]{0,100}(?: -?[_a-zA-Z][_a-zA-Z0-9-]{0,100})*)?!(?:(?:[a-zA-Z][_a-zA-Z0-9-]{0,100})!)?)?)?",
    ]


def test_fswquery_prefix_or_search():
    assert fswquery_regex("QAS105uuoS107uuT") == [
        "(?:A(?:S105[0-5][0-9a-f]|S107[0-5][0-9a-f])(?:S00000|S[123][0-9a-f]{2}[0-5][0-9a-f])*)[BLMR][0-9]{3}x[0-9]{3}(?:S[123][0-9a-f]{2}[0-5][0-9a-f][0-9]{3}x[0-9]{3})*"
    ]


def test_fswquery_signbox_or_search():
    assert fswquery_regex("QS105uuoS107uu") == [
        "(?:A(?:S00000|S[123][0-9a-f]{2}[0-5][0-9a-f])+)?[BLMR][0-9]{3}x[0-9]{3}(?:S[123][0-9a-f]{2}[0-5][0-9a-f][0-9]{3}x[0-9]{3})*(?:S105[0-5][0-9a-f]|S107[0-5][0-9a-f])[0-9]{3}x[0-9]{3}(?:S[123][0-9a-f]{2}[0-5][0-9a-f][0-9]{3}x[0-9]{3})*"
    ]


# ------------------------------------------------------------------ #
# FSW Query Results Tests
# ------------------------------------------------------------------ #

signtext = "AS10011S10019S2e704S2e748M525x535S2e748483x510S10011501x466S2e704510x500S10019476x475 AS15a21S15a07S21100S2df04S2df14M521x538S15a07494x488S15a21498x489S2df04498x517S2df14497x461S21100479x486 AS1f010S10018S20600M519x524S10018485x494S1f010490x494S20600481x476 S38800464x496 AS10e00M507x515S10e00492x485 AS15d41S15a36S21100S26505M535x521S15d41464x479S15a36474x503S21100507x491S26505522x508 S38700463x496 AS10020M508x515S10020493x485 AS10011S28108S30a00M540x519S30a00482x482S10011519x489S28108519x461 AS10e00S10e08S20500S27100S2711cS20500S2fc00S30006S30002M544x527S10e08470x497S10e00516x497S30006482x482S20500519x484S20500471x484S27100504x464S2711c451x463S30002482x482S2fc00491x453 S38700463x496 AS10e20M508x515S10e20493x485 AS10011S28108S30a00M540x519S30a00482x482S10011519x489S28108519x461 AS10120S15a3aS26a02S20e00M529x518S15a3a502x506S20e00487x495S10120507x483S26a02471x491 AS10020S2df04S10000M527x516S10000512x486S10020473x486S2df04489x485 AS10012S19205S22a04S20e00M529x525S10012499x477S20e00499x491S19205472x476S22a04499x510 S38800464x496 AS15a21S2a20cS15a01S15a07M538x518S15a21515x483S15a07463x482S15a01466x483S2a20c493x490 AS10011S10019S2eb04S2eb48M523x536S2eb48485x504S10011502x463S2eb04507x497S10019477x472 AS19a00S19a08S22a04S22a14S2fb04M534x521S22a14475x503S19a00506x479S19a08467x479S22a04514x504S2fb04493x515 S38800464x496 AS1eb20S15a37S26507S26507S15a10S15a18S22b04S22b14M530x550S15a37470x456S15a10515x523S15a18481x523S1eb20490x468S22b14479x488S26507504x450S22b04514x489S26507516x460 AS1d117S26505S1d417M539x531S1d117460x468S1d417514x506S26505491x492 M517x522S1000a487x507S10041483x479 S38700463x496 AS20320S22e04M509x519S20320493x481S22e04492x501 S38800464x496 M532x516S1ce20469x485S20320495x500S18620514x486 S38700463x496 M533x538S1f110504x523S34d00482x482 M554x518S1920a481x484S19202501x484S26606524x483S26612446x483S20500496x507 S38700463x496 AS15d02S15d0aS20e00S22f00M522x524S22f00487x477S15d02495x500S15d0a479x505S20e00493x493 AS11500S20308S20e00S26a02S34600M525x562S20308503x547S11500510x515S20e00495x531S26a02478x525S34600482x482 S38700463x496 M551x542S1dc2f448x465S1dc01482x459S26605502x488S26615467x490S1e101526x509S1e12f488x510 AS18040S18048S2eb08S2eb4cS2fb00M532x538S18040501x523S18048467x511S2eb4c477x470S2eb08506x483S2fb00494x462 S38800464x496 M532x516S1ce20469x485S20320495x500S18620514x486 AS19a00S19a08S22a04S22a14S2fb04M534x521S22a14475x503S19a00506x479S19a08467x479S22a04514x504S2fb04493x515 S38700463x496 AS10011S10019S2eb04S2eb48M523x536S2eb48485x504S10011502x463S2eb04507x497S10019477x472 AS1eb20S15a06S29b0bM516x531S15a06484x468S1eb20492x483S29b0b484x496 AS20350S20358S22f04S22f14S30114M528x565S20350508x530S20358477x530S22f04503x551S22f14471x551S30114482x477 S38800464x496"

signlines = """AS10011S10019S2e704S2e748M525x535S2e748483x510S10011501x466S2e704510x500S10019476x475 this line here
AS15a21S15a07S21100S2df04S2df14M521x538S15a07494x488S15a21498x489S2df04498x517S2df14497x461S21100479x486 this line here
AS1f010S10018S20600M519x524S10018485x494S1f010490x494S20600481x476 this line here
S38800464x496 this line here
AS10e00M507x515S10e00492x485 this line here
AS15d41S15a36S21100S26505M535x521S15d41464x479S15a36474x503S21100507x491S26505522x508 this line here
S38700463x496 this line here
AS10020M508x515S10020493x485 this line here
AS10011S28108S30a00M540x519S30a00482x482S10011519x489S28108519x461 this line here
AS10e00S10e08S20500S27100S2711cS20500S2fc00S30006S30002M544x527S10e08470x497S10e00516x497S30006482x482S20500519x484S20500471x484S27100504x464S2711c451x463S30002482x482S2fc00491x453 this line here
S38700463x496 this line here
AS10e20M508x515S10e20493x485 this line here
AS10011S28108S30a00M540x519S30a00482x482S10011519x489S28108519x461 this line here
AS10120S15a3aS26a02S20e00M529x518S15a3a502x506S20e00487x495S10120507x483S26a02471x491 this line here
AS10020S2df04S10000M527x516S10000512x486S10020473x486S2df04489x485 this line here
AS10012S19205S22a04S20e00M529x525S10012499x477S20e00499x491S19205472x476S22a04499x510 this line here
S38800464x496 this line here
AS15a21S2a20cS15a01S15a07M538x518S15a21515x483S15a07463x482S15a01466x483S2a20c493x490 this line here
AS10011S10019S2eb04S2eb48M523x536S2eb48485x504S10011502x463S2eb04507x497S10019477x472 this line here
AS19a00S19a08S22a04S22a14S2fb04M534x521S22a14475x503S19a00506x479S19a08467x479S22a04514x504S2fb04493x515 this line here
S38800464x496 this line here
AS1eb20S15a37S26507S26507S15a10S15a18S22b04S22b14M530x550S15a37470x456S15a10515x523S15a18481x523S1eb20490x468S22b14479x488S26507504x450S22b04514x489S26507516x460 this line here
AS1d117S26505S1d417M539x531S1d117460x468S1d417514x506S26505491x492 this line here
M517x522S1000a487x507S10041483x479 this line here
S38700463x496 this line here
AS20320S22e04M509x519S20320493x481S22e04492x501 this line here
S38800464x496 this line here
M532x516S1ce20469x485S20320495x500S18620514x486 this line here
S38700463x496 this line here
M533x538S1f110504x523S34d00482x482 this line here
M554x518S1920a481x484S19202501x484S26606524x483S26612446x483S20500496x507 this line here
S38700463x496 this line here
AS15d02S15d0aS20e00S22f00M522x524S22f00487x477S15d02495x500S15d0a479x505S20e00493x493 this line here
AS11500S20308S20e00S26a02S34600M525x562S20308503x547S11500510x515S20e00495x531S26a02478x525S34600482x482 this line here
S38700463x496 this line here
M551x542S1dc2f448x465S1dc01482x459S26605502x488S26615467x490S1e101526x509S1e12f488x510 this line here
AS18040S18048S2eb08S2eb4cS2fb00M532x538S18040501x523S18048467x511S2eb4c477x470S2eb08506x483S2fb00494x462 this line here
S38800464x496 this line here
M532x516S1ce20469x485S20320495x500S18620514x486 this line here
AS19a00S19a08S22a04S22a14S2fb04M534x521S22a14475x503S19a00506x479S19a08467x479S22a04514x504S2fb04493x515 this line here
S38700463x496 this line here
AS10011S10019S2eb04S2eb48M523x536S2eb48485x504S10011502x463S2eb04507x497S10019477x472 this line here
AS1eb20S15a06S29b0bM516x531S15a06484x468S1eb20492x483S29b0b484x496 this line here
AS20350S20358S22f04S22f14S30114M528x565S20350508x530S20358477x530S22f04503x551S22f14471x551S30114482x477 this line here
S38800464x496 this line here"""


def test_fswquery_results_matching_signs():
    assert fswquery_results("QAS1eb20T", signtext) == [
        "AS1eb20S15a37S26507S26507S15a10S15a18S22b04S22b14M530x550S15a37470x456S15a10515x523S15a18481x523S1eb20490x468S22b14479x488S26507504x450S22b04514x489S26507516x460",
        "AS1eb20S15a06S29b0bM516x531S15a06484x468S1eb20492x483S29b0b484x496",
    ]
    assert fswquery_results("QAS20350S203uuTS22f04S301uu480x480", signtext) == [
        "AS20350S20358S22f04S22f14S30114M528x565S20350508x530S20358477x530S22f04503x551S22f14471x551S30114482x477"
    ]


def test_fswquery_lines_matching_sign_start():
    assert fswquery_lines("QAS1eb20T", signlines) == [
        "AS1eb20S15a37S26507S26507S15a10S15a18S22b04S22b14M530x550S15a37470x456S15a10515x523S15a18481x523S1eb20490x468S22b14479x488S26507504x450S22b04514x489S26507516x460 this line here",
        "AS1eb20S15a06S29b0bM516x531S15a06484x468S1eb20492x483S29b0b484x496 this line here",
    ]
    assert fswquery_lines("QAS20350S203uuTS22f04S301uu480x480", signlines) == [
        "AS20350S20358S22f04S22f14S30114M528x565S20350508x530S20358477x530S22f04503x551S22f14471x551S30114482x477 this line here"
    ]
