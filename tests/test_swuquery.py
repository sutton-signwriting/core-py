"""
pytest suite for the parse functions.
"""

from __future__ import annotations

import pytest

# ------------------------------------------------------------------ #
# Import the public API
# ------------------------------------------------------------------ #
from sutton_signwriting_core import (
    swuquery_parse,
    swuquery_compose,
    swu_to_query,
    swuquery_range,
    swuquery_regex,
    swuquery_results,
    swuquery_lines,
)


# ------------------------------------------------------------------ #
# SWU Query Parsing Tests
# ------------------------------------------------------------------ #


def test_swuquery_parse_generic():
    assert swuquery_parse("Q") == {"query": True}
    assert swuquery_parse("Q-") == {"query": True, "style": True}


def test_swuquery_parse_prefix_basic():
    assert swuquery_parse("QT") == {"query": True, "prefix": {"required": True}}
    assert swuquery_parse("QT-") == {
        "query": True,
        "prefix": {"required": True},
        "style": True,
    }


def test_swuquery_parse_prefix_parts():
    assert swuquery_parse("QA񀀁R񀀁񆆑񆇡T") == {
        "query": True,
        "prefix": {"required": True, "parts": ["񀀁", ["񀀁", "񆆑"], "񆇡"]},
    }


def test_swuquery_parse_prefix_with_or():
    assert swuquery_parse("QA񀀁oR񀀁񆆑񆇡T") == {
        "query": True,
        "prefix": {"required": True, "parts": [["or_list", "񀀁", ["񀀁", "񆆑"]], "񆇡"]},
    }


def test_swuquery_parse_signbox_basic():
    assert swuquery_parse("Q񆀁") == {"query": True, "signbox": [{"symbol": "񆀁"}]}


def test_swuquery_parse_signbox_with_coord():
    assert swuquery_parse("Q񆀁fr𝤆𝤆") == {
        "query": True,
        "signbox": [{"symbol": "񆀁fr", "coord": [500, 500]}],
    }


def test_swuquery_parse_signbox_range():
    assert swuquery_parse("QR񀀁񀇡") == {"query": True, "signbox": [{"range": ["񀀁", "񀇡"]}]}


def test_swuquery_parse_signbox_range_with_coord():
    assert swuquery_parse("QR񀀁񀇡𝤆𝤆") == {
        "query": True,
        "signbox": [{"range": ["񀀁", "񀇡"], "coord": [500, 500]}],
    }


def test_swuquery_parse_signbox_mixed():
    assert swuquery_parse("Q񆀁rR񀀁񀇡𝤆𝤆") == {
        "query": True,
        "signbox": [{"symbol": "񆀁r"}, {"range": ["񀀁", "񀇡"], "coord": [500, 500]}],
    }


def test_swuquery_parse_signbox_with_or():
    assert swuquery_parse("Q񆀁roR񀀁񀇡𝤆𝤆") == {
        "query": True,
        "signbox": [{"or_list": ["񆀁r", ["񀀁", "񀇡"]], "coord": [500, 500]}],
    }


@pytest.mark.parametrize("invalid_input", ["a"])
def test_swuquery_parse_invalid(invalid_input):
    assert swuquery_parse(invalid_input) == {"query": False}


# ------------------------------------------------------------------ #
# SWU Query Compose Tests (inverse of swuquery/swuquery-parse.test.js)
# ------------------------------------------------------------------ #


def test_swuquery_compose_generic():
    assert swuquery_compose({"query": True}) == "Q"
    assert swuquery_compose({"query": True, "style": True}) == "Q-"


def test_swuquery_compose_prefix_basic():
    assert swuquery_compose({"query": True, "prefix": {"required": True}}) == "QT"
    assert (
        swuquery_compose({"query": True, "prefix": {"required": True}, "style": True})
        == "QT-"
    )


def test_swuquery_compose_prefix_parts():
    assert (
        swuquery_compose(
            {
                "query": True,
                "prefix": {"required": True, "parts": ["񀀁", ["񀀁", "񆆑"], "񆇡"]},
            }
        )
        == "QA񀀁R񀀁񆆑񆇡T"
    )


def test_swuquery_compose_prefix_with_or():
    assert (
        swuquery_compose(
            {
                "query": True,
                "prefix": {
                    "required": True,
                    "parts": [["or_list", "񀀁", ["񀀁", "񆆑"]], "񆇡"],
                },
            }
        )
        == "QA񀀁oR񀀁񆆑񆇡T"
    )


def test_swuquery_compose_signbox_basic():
    assert swuquery_compose({"query": True, "signbox": [{"symbol": "񆀁"}]}) == "Q񆀁"


def test_swuquery_compose_signbox_with_coord():
    assert (
        swuquery_compose(
            {"query": True, "signbox": [{"symbol": "񆀁fr", "coord": [500, 500]}]}
        )
        == "Q񆀁fr𝤆𝤆"
    )


def test_swuquery_compose_signbox_range():
    assert (
        swuquery_compose({"query": True, "signbox": [{"range": ["񀀁", "񀇡"]}]}) == "QR񀀁񀇡"
    )


def test_swuquery_compose_signbox_range_with_coord():
    assert (
        swuquery_compose(
            {"query": True, "signbox": [{"range": ["񀀁", "񀇡"], "coord": [500, 500]}]}
        )
        == "QR񀀁񀇡𝤆𝤆"
    )


def test_swuquery_compose_signbox_mixed():
    assert (
        swuquery_compose(
            {
                "query": True,
                "signbox": [
                    {"symbol": "񆀁r"},
                    {"range": ["񀀁", "񀇡"], "coord": [500, 500]},
                ],
            }
        )
        == "Q񆀁rR񀀁񀇡𝤆𝤆"
    )


def test_swuquery_compose_signbox_with_or():
    assert (
        swuquery_compose(
            {
                "query": True,
                "signbox": [{"or_list": ["񆀁r", ["񀀁", "񀇡"]], "coord": [500, 500]}],
            }
        )
        == "Q񆀁roR񀀁񀇡𝤆𝤆"
    )


def test_swuquery_compose_full_example():
    assert (
        swuquery_compose(
            {
                "query": True,
                "prefix": {"required": True, "parts": ["񀀁", ["񀀁", "񆆑"], "񆇡"]},
                "signbox": [
                    {"symbol": "񆀁"},
                    {"range": ["񀀁", "񀇱"], "coord": [500, 500]},
                ],
                "variance": 5,
                "style": True,
            }
        )
        == "QA񀀁R񀀁񆆑񆇡T񆀁R񀀁񀇱𝤆𝤆V5-"
    )


@pytest.mark.parametrize("invalid_input", [{}, {"query": False}])
def test_swuquery_compose_invalid(invalid_input):
    assert swuquery_compose(invalid_input) is None


# ------------------------------------------------------------------ #
# SWU to Query Tests
# ------------------------------------------------------------------ #


def test_swu_to_query():
    assert swu_to_query("𝠀񀀒񀀚񋚥񋛩𝠃𝤟𝤩񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭", "ASL") == "QA񀀒񀀚񋚥񋛩T񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭"
    assert swu_to_query("𝠀񀀒񀀚񋚥񋛩𝠃𝤟𝤩񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭", "a") == "QA񀀒fr񀀚fr񋚥fr񋛩frT"
    assert swu_to_query("𝠀񀀒񀀚񋚥񋛩𝠃𝤟𝤩񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭", "sL") == "Q񋛩fr𝣵𝤐񀀒fr𝤇𝣤񋚥fr𝤐𝤆񀀚fr𝣮𝣭"


# ------------------------------------------------------------------ #
# SWU Query Range Tests
# ------------------------------------------------------------------ #


def test_swuquery_range_symbols():
    assert swuquery_range("񀀁", "񀇡") == "[\\U00040001-\\U000401E1]"


def test_swuquery_range_numbers():
    assert swuquery_range("𝣔", "𝤸") == "[\\U0001D8D4-\\U0001D938]"


# ------------------------------------------------------------------ #
# SWU Query Regex Tests
# ------------------------------------------------------------------ #


def test_swuquery_regex_general():
    assert swuquery_regex("Q") == [
        "(?:\\U0001D800(?:\\U00040000|[\\U00040001-\\U0004F480])+)?[\\U0001D801-\\U0001D804][\\U0001D80C-\\U0001D9FF]{2}(?:[\\U00040001-\\U0004F480][\\U0001D80C-\\U0001D9FF]{2})*"
    ]


def test_swuquery_regex_signbox():
    assert swuquery_regex("Q񀀒") == [
        "(?:\\U0001D800(?:\\U00040000|[\\U00040001-\\U0004F480])+)?[\\U0001D801-\\U0001D804][\\U0001D80C-\\U0001D9FF]{2}(?:[\\U00040001-\\U0004F480][\\U0001D80C-\\U0001D9FF]{2})*\\U00040012[\\U0001D80C-\\U0001D9FF]{2}(?:[\\U00040001-\\U0004F480][\\U0001D80C-\\U0001D9FF]{2})*"
    ]
    assert swuquery_regex("Q񀀒r") == [
        "(?:\\U0001D800(?:\\U00040000|[\\U00040001-\\U0004F480])+)?[\\U0001D801-\\U0001D804][\\U0001D80C-\\U0001D9FF]{2}(?:[\\U00040001-\\U0004F480][\\U0001D80C-\\U0001D9FF]{2})*[\\U00040011-\\U00040020][\\U0001D80C-\\U0001D9FF]{2}(?:[\\U00040001-\\U0004F480][\\U0001D80C-\\U0001D9FF]{2})*"
    ]
    assert swuquery_regex("Q񀀑f") == [
        "(?:\\U0001D800(?:\\U00040000|[\\U00040001-\\U0004F480])+)?[\\U0001D801-\\U0001D804][\\U0001D80C-\\U0001D9FF]{2}(?:[\\U00040001-\\U0004F480][\\U0001D80C-\\U0001D9FF]{2})*(?:\\U00040001|\\U00040011|\\U00040021|\\U00040031|\\U00040041|\\U00040051)[\\U0001D80C-\\U0001D9FF]{2}(?:[\\U00040001-\\U0004F480][\\U0001D80C-\\U0001D9FF]{2})*"
    ]
    assert swuquery_regex("QR񋔡񋮁") == [
        "(?:\\U0001D800(?:\\U00040000|[\\U00040001-\\U0004F480])+)?[\\U0001D801-\\U0001D804][\\U0001D80C-\\U0001D9FF]{2}(?:[\\U00040001-\\U0004F480][\\U0001D80C-\\U0001D9FF]{2})*[\\U0004B521-\\U0004BBE0][\\U0001D80C-\\U0001D9FF]{2}(?:[\\U00040001-\\U0004F480][\\U0001D80C-\\U0001D9FF]{2})*"
    ]


def test_swuquery_regex_prefix():
    assert swuquery_regex("QA񀀒T") == [
        "\\U0001D800\\U00040012(?:\\U00040000|[\\U00040001-\\U0004F480])*[\\U0001D801-\\U0001D804][\\U0001D80C-\\U0001D9FF]{2}(?:[\\U00040001-\\U0004F480][\\U0001D80C-\\U0001D9FF]{2})*"
    ]
    assert swuquery_regex("QA񀀑rT") == [
        "\\U0001D800[\\U00040011-\\U00040020](?:\\U00040000|[\\U00040001-\\U0004F480])*[\\U0001D801-\\U0001D804][\\U0001D80C-\\U0001D9FF]{2}(?:[\\U00040001-\\U0004F480][\\U0001D80C-\\U0001D9FF]{2})*"
    ]


def test_swuquery_regex_prefix_and_signbox():
    assert swuquery_regex("QA񀀑rT񀀓𝤅𝣯񆕁𝤅𝣽") == [
        "\\U0001D800[\\U00040011-\\U00040020](?:\\U00040000|[\\U00040001-\\U0004F480])*[\\U0001D801-\\U0001D804][\\U0001D80C-\\U0001D9FF]{2}(?:[\\U00040001-\\U0004F480][\\U0001D80C-\\U0001D9FF]{2})*\\U00040013[\\U0001D8F1-\\U0001D919][\\U0001D8DB-\\U0001D903](?:[\\U00040001-\\U0004F480][\\U0001D80C-\\U0001D9FF]{2})*",
        "\\U0001D800[\\U00040011-\\U00040020](?:\\U00040000|[\\U00040001-\\U0004F480])*[\\U0001D801-\\U0001D804][\\U0001D80C-\\U0001D9FF]{2}(?:[\\U00040001-\\U0004F480][\\U0001D80C-\\U0001D9FF]{2})*\\U00046541[\\U0001D8F1-\\U0001D919][\\U0001D8E9-\\U0001D911](?:[\\U00040001-\\U0004F480][\\U0001D80C-\\U0001D9FF]{2})*",
    ]


def test_swuquery_regex_prefix_or_search():
    assert swuquery_regex("QA񀀒o񂇢T") == [
        "\\U0001D800(?:\\U00040012|\\U000421E2)(?:\\U00040000|[\\U00040001-\\U0004F480])*[\\U0001D801-\\U0001D804][\\U0001D80C-\\U0001D9FF]{2}(?:[\\U00040001-\\U0004F480][\\U0001D80C-\\U0001D9FF]{2})*"
    ]


def test_swuquery_regex_signbox_or_search():
    assert swuquery_regex("Q񀀒o񋛩𝣵𝤐") == [
        "(?:\\U0001D800(?:\\U00040000|[\\U00040001-\\U0004F480])+)?[\\U0001D801-\\U0001D804][\\U0001D80C-\\U0001D9FF]{2}(?:[\\U00040001-\\U0004F480][\\U0001D80C-\\U0001D9FF]{2})*(?:\\U00040012|\\U0004B6E9)[\\U0001D8E1-\\U0001D909][\\U0001D8FC-\\U0001D924](?:[\\U00040001-\\U0004F480][\\U0001D80C-\\U0001D9FF]{2})*"
    ]


# ----------------------------
# SWU Query Results
# ----------------------------

# Paste this into the test file for swuquery.py (e.g., test_swuquery.py)

signtext = "𝠀񀀒񀀚񋚥񋛩𝠃𝤟𝤩񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭 𝠀񂇢񂇈񆙡񋎥񋎵𝠃𝤛𝤬񂇈𝤀𝣺񂇢𝤄𝣻񋎥𝤄𝤗񋎵𝤃𝣟񆙡𝣱𝣸 𝠀񅨑񀀙񆉁𝠃𝤙𝤞񀀙𝣷𝤀񅨑𝣼𝤀񆉁𝣳𝣮 񏌁𝣢𝤂 𝠀񀕁𝠃𝤍𝤕񀕁𝣾𝣷 𝠀񂌢񂇷񆙡񈗦𝠃𝤩𝤛񂌢𝣢𝣱񂇷𝣬𝤉񆙡𝤍𝣽񈗦𝤜𝤎 񏊡𝣡𝤂 𝠀񀀡𝠃𝤎𝤕񀀡𝣿𝣷 𝠀񀀒񉁩񌏁𝠃𝤮𝤙񌏁𝣴𝣴񀀒𝤙𝣻񉁩𝤙𝣟 𝠀񀕁񀕉񆇡񈩡񈩽񆇡񋺁񌀇񌀃𝠃𝤲𝤡񀕉𝣨𝤃񀕁𝤖𝤃񌀇𝣴𝣴񆇡𝤙𝣶񆇡𝣩𝣶񈩡𝤊𝣢񈩽𝣕𝣡񌀃𝣴𝣴񋺁𝣽𝣗 񏊡𝣡𝤂 𝠀񀕡𝠃𝤎𝤕񀕡𝣿𝣷 𝠀񀀒񉁩񌏁𝠃𝤮𝤙񌏁𝣴𝣴񀀒𝤙𝣻񉁩𝤙𝣟 𝠀񀂁񂇻񈟃񆕁𝠃𝤣𝤘񂇻𝤈𝤌񆕁𝣹𝤁񀂁𝤍𝣵񈟃𝣩𝣽 𝠀񀀡񋎥񀀁𝠃𝤡𝤖񀀁𝤒𝣸񀀡𝣫𝣸񋎥𝣻𝣷 𝠀񀀓񃛆񆿅񆕁𝠃𝤣𝤟񀀓𝤅𝣯񆕁𝤅𝣽񃛆𝣪𝣮񆿅𝤅𝤐 񏌁𝣢𝤂 𝠀񂇢񉳍񂇂񂇈𝠃𝤬𝤘񂇢𝤕𝣵񂇈𝣡𝣴񂇂𝣤𝣵񉳍𝣿𝣼 𝠀񀀒񀀚񋠥񋡩𝠃𝤝𝤪񋡩𝣷𝤊񀀒𝤈𝣡񋠥𝤍𝤃񀀚𝣯𝣪 𝠀񃧁񃧉񆿅񆿕񋸥𝠃𝤨𝤛񆿕𝣭𝤉񃧁𝤌𝣱񃧉𝣥𝣱񆿅𝤔𝤊񋸥𝣿𝤕 񏌁𝣢𝤂 𝠀񅡁񂇸񈗨񈗨񂇑񂇙񇀥񇀵𝠃𝤤𝤸񂇸𝣨𝣚񂇑𝤕𝤝񂇙𝣳𝤝񅡁𝣼𝣦񇀵𝣱𝣺񈗨𝤊𝣔񇀥𝤔𝣻񈗨𝤖𝣞 𝠀񄹸񈗦񄾘𝠃𝤭𝤥񄹸𝣞𝣦񄾘𝤔𝤌񈗦𝣽𝣾 𝠃𝤗𝤜񀀋𝣹𝤍񀁂𝣵𝣱 񏊡𝣡𝤂 𝠀񆅁񇅅𝠃𝤏𝤙񆅁𝣿𝣳񇅅𝣾𝤇 񏌁𝣢𝤂 𝠃𝤦𝤖񄵡𝣧𝣷񆅁𝤁𝤆񃉡𝤔𝣸 񏊡𝣡𝤂 𝠃𝤧𝤬񅩱𝤊𝤝񍳡𝣴𝣴 𝠃𝤼𝤘񃛋𝣳𝣶񃛃𝤇𝣶񈙇𝤞𝣵񈙓𝣐𝣵񆇡𝤂𝤍 񏊡𝣡𝤂 𝠀񂋣񂋫񆕁񇆡𝠃𝤜𝤞񇆡𝣹𝣯񂋣𝤁𝤆񂋫𝣱𝤋񆕁𝣿𝣿 𝠀񀟡񆄩񆕁񈟃񍩁𝠃𝤟𝥄񆄩𝤉𝤵񀟡𝤐𝤕񆕁𝤁𝤥񈟃𝣰𝤟񍩁𝣴𝣴 񏊡𝣡𝤂 𝠃𝤹𝤰񅊰𝣒𝣣񅊂𝣴𝣝񈙆𝤈𝣺񈙖𝣥𝣼񅑢𝤠𝤏񅒐𝣺𝤐 𝠀񃁁񃁉񋠩񋡭񋸡𝠃𝤦𝤬񃁁𝤇𝤝񃁉𝣥𝤑񋡭𝣯𝣨񋠩𝤌𝣵񋸡𝤀𝣠 񏌁𝣢𝤂 𝠃𝤦𝤖񄵡𝣧𝣷񆅁𝤁𝤆񃉡𝤔𝣸 𝠀񃧁񃧉񆿅񆿕񋸥𝠃𝤨𝤛񆿕𝣭𝤉񃧁𝤌𝣱񃧉𝣥𝣱񆿅𝤔𝤊񋸥𝣿𝤕 񏊡𝣡𝤂 𝠀񀀒񀀚񋠥񋡩𝠃𝤝𝤪񋡩𝣷𝤊񀀒𝤈𝣡񋠥𝤍𝤃񀀚𝣯𝣪 𝠀񅡁񂇇񉨬𝠃𝤖𝤥񂇇𝣶𝣦񅡁𝣾𝣵񉨬𝣶𝤂 𝠀񆅱񆅹񇆥񇆵񌁵𝠃𝤢𝥇񆅱𝤎𝤤񆅹𝣯𝤤񇆥𝤉𝤹񇆵𝣩𝤹񌁵𝣴𝣯 񏌁𝣢𝤂"

signlines = """𝠀񀀒񀀚񋚥񋛩𝠃𝤟𝤩񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭 this line here
𝠀񂇢񂇈񆙡񋎥񋎵𝠃𝤛𝤬񂇈𝤀𝣺񂇢𝤄𝣻񋎥𝤄𝤗񋎵𝤃𝣟񆙡𝣱𝣸 this line here
𝠀񅨑񀀙񆉁𝠃𝤙𝤞񀀙𝣷𝤀񅨑𝣼𝤀񆉁𝣳𝣮 this line here
񏌁𝣢𝤂 this line here
𝠀񀕁𝠃𝤍𝤕񀕁𝣾𝣷 this line here
𝠀񂌢񂇷񆙡񈗦𝠃𝤩𝤛񂌢𝣢𝣱񂇷𝣬𝤉񆙡𝤍𝣽񈗦𝤜𝤎 this line here
񏊡𝣡𝤂 this line here
𝠀񀀡𝠃𝤎𝤕񀀡𝣿𝣷 this line here
𝠀񀀒񉁩񌏁𝠃𝤮𝤙񌏁𝣴𝣴񀀒𝤙𝣻񉁩𝤙𝣟 this line here
𝠀񀕁񀕉񆇡񈩡񈩽񆇡񋺁񌀇񌀃𝠃𝤲𝤡񀕉𝣨𝤃񀕁𝤖𝤃񌀇𝣴𝣴񆇡𝤙𝣶񆇡𝣩𝣶񈩡𝤊𝣢񈩽𝣕𝣡񌀃𝣴𝣴񋺁𝣽𝣗 this line here
񏊡𝣡𝤂 this line here
𝠀񀕡𝠃𝤎𝤕񀕡𝣿𝣷 this line here
𝠀񀀒񉁩񌏁𝠃𝤮𝤙񌏁𝣴𝣴񀀒𝤙𝣻񉁩𝤙𝣟 this line here
𝠀񀂁񂇻񈟃񆕁𝠃𝤣𝤘񂇻𝤈𝤌񆕁𝣹𝤁񀂁𝤍𝣵񈟃𝣩𝣽 this line here
𝠀񀀡񋎥񀀁𝠃𝤡𝤖񀀁𝤒𝣸񀀡𝣫𝣸񋎥𝣻𝣷 this line here
𝠀񀀓񃛆񆿅񆕁𝠃𝤣𝤟񀀓𝤅𝣯񆕁𝤅𝣽񃛆𝣪𝣮񆿅𝤅𝤐 this line here
񏌁𝣢𝤂 this line here
𝠀񂇢񉳍񂇂񂇈𝠃𝤬𝤘񂇢𝤕𝣵񂇈𝣡𝣴񂇂𝣤𝣵񉳍𝣿𝣼 this line here
𝠀񀀒񀀚񋠥񋡩𝠃𝤝𝤪񋡩𝣷𝤊񀀒𝤈𝣡񋠥𝤍𝤃񀀚𝣯𝣪 this line here
𝠀񃧁񃧉񆿅񆿕񋸥𝠃𝤨𝤛񆿕𝣭𝤉񃧁𝤌𝣱񃧉𝣥𝣱񆿅𝤔𝤊񋸥𝣿𝤕 this line here
񏌁𝣢𝤂 this line here
𝠀񅡁񂇸񈗨񈗨񂇑񂇙񇀥񇀵𝠃𝤤𝤸񂇸𝣨𝣚񂇑𝤕𝤝񂇙𝣳𝤝񅡁𝣼𝣦񇀵𝣱𝣺񈗨𝤊𝣔񇀥𝤔𝣻񈗨𝤖𝣞 this line here
𝠀񄹸񈗦񄾘𝠃𝤭𝤥񄹸𝣞𝣦񄾘𝤔𝤌񈗦𝣽𝣾 this line here
𝠃𝤗𝤜񀀋𝣹𝤍񀁂𝣵𝣱 this line here
񏊡𝣡𝤂 this line here
𝠀񆅁񇅅𝠃𝤏𝤙񆅁𝣿𝣳񇅅𝣾𝤇 this line here
񏌁𝣢𝤂 this line here
𝠃𝤦𝤖񄵡𝣧𝣷񆅁𝤁𝤆񃉡𝤔𝣸 this line here
񏊡𝣡𝤂 this line here
𝠃𝤧𝤬񅩱𝤊𝤝񍳡𝣴𝣴 this line here
𝠃𝤼𝤘񃛋𝣳𝣶񃛃𝤇𝣶񈙇𝤞𝣵񈙓𝣐𝣵񆇡𝤂𝤍 this line here
񏊡𝣡𝤂 this line here
𝠀񂋣񂋫񆕁񇆡𝠃𝤜𝤞񇆡𝣹𝣯񂋣𝤁𝤆񂋫𝣱𝤋񆕁𝣿𝣿 this line here
𝠀񀟡񆄩񆕁񈟃񍩁𝠃𝤟𝥄񆄩𝤉𝤵񀟡𝤐𝤕񆕁𝤁𝤥񈟃𝣰𝤟񍩁𝣴𝣴 this line here
񏊡𝣡𝤂 this line here
𝠃𝤹𝤰񅊰𝣒𝣣񅊂𝣴𝣝񈙆𝤈𝣺񈙖𝣥𝣼񅑢𝤠𝤏񅒐𝣺𝤐 this line here
𝠀񃁁񃁉񋠩񋡭񋸡𝠃𝤦𝤬񃁁𝤇𝤝񃁉𝣥𝤑񋡭𝣯𝣨񋠩𝤌𝣵񋸡𝤀𝣠 this line here
񏌁𝣢𝤂 this line here
𝠃𝤦𝤖񄵡𝣧𝣷񆅁𝤁𝤆񃉡𝤔𝣸 this line here
𝠀񃧁񃧉񆿅񆿕񋸥𝠃𝤨𝤛񆿕𝣭𝤉񃧁𝤌𝣱񃧉𝣥𝣱񆿅𝤔𝤊񋸥𝣿𝤕 this line here
񏊡𝣡𝤂 this line here
𝠀񀀒񀀚񋠥񋡩𝠃𝤝𝤪񋡩𝣷𝤊񀀒𝤈𝣡񋠥𝤍𝤃񀀚𝣯𝣪 this line here
𝠀񅡁񂇇񉨬𝠃𝤖𝤥񂇇𝣶𝣦񅡁𝣾𝣵񉨬𝣶𝤂 this line here
𝠀񆅱񆅹񇆥񇆵񌁵𝠃𝤢𝥇񆅱𝤎𝤤񆅹𝣯𝤤񇆥𝤉𝤹񇆵𝣩𝤹񌁵𝣴𝣯 this line here
񏌁𝣢𝤂 this line here"""


def test_swuquery_results_matching_signs():
    assert swuquery_results("QA񅡁T", signtext) == [
        "𝠀񅡁񂇸񈗨񈗨񂇑񂇙񇀥񇀵𝠃𝤤𝤸񂇸𝣨𝣚񂇑𝤕𝤝񂇙𝣳𝤝񅡁𝣼𝣦񇀵𝣱𝣺񈗨𝤊𝣔񇀥𝤔𝣻񈗨𝤖𝣞",
        "𝠀񅡁񂇇񉨬𝠃𝤖𝤥񂇇𝣶𝣦񅡁𝣾𝣵񉨬𝣶𝤂",
    ]
    assert swuquery_results("QA񆅱񆅹frT񇆥񌁵fr𝣲𝣲", signtext) == ["𝠀񆅱񆅹񇆥񇆵񌁵𝠃𝤢𝥇񆅱𝤎𝤤񆅹𝣯𝤤񇆥𝤉𝤹񇆵𝣩𝤹񌁵𝣴𝣯"]


def test_swuquery_lines_matching_sign_start():
    assert swuquery_lines("QA񅡁T", signlines) == [
        "𝠀񅡁񂇸񈗨񈗨񂇑񂇙񇀥񇀵𝠃𝤤𝤸񂇸𝣨𝣚񂇑𝤕𝤝񂇙𝣳𝤝񅡁𝣼𝣦񇀵𝣱𝣺񈗨𝤊𝣔񇀥𝤔𝣻񈗨𝤖𝣞 this line here",
        "𝠀񅡁񂇇񉨬𝠃𝤖𝤥񂇇𝣶𝣦񅡁𝣾𝣵񉨬𝣶𝤂 this line here",
    ]
    assert swuquery_lines("QA񆅱񆅹frT񇆥񌁵fr𝣲𝣲", signlines) == [
        "𝠀񆅱񆅹񇆥񇆵񌁵𝠃𝤢𝥇񆅱𝤎𝤤񆅹𝣯𝤤񇆥𝤉𝤹񇆵𝣩𝤹񌁵𝣴𝣯 this line here"
    ]
