"""
pytest suite for the convert functions.
"""

from __future__ import annotations

import pytest

# ------------------------------------------------------------------ #
# Import the public API
# ------------------------------------------------------------------ #
from sutton_signwriting_core import (
    swu_to_mark,
    mark_to_swu,
    swu_to_num,
    num_to_swu,
    swu_to_coord,
    coord_to_swu,
    fsw_to_coord,
    coord_to_fsw,
    swu_to_code,
    code_to_swu,
    swu_to_id,
    id_to_swu,
    key_to_id,
    id_to_key,
    swu_to_key,
    key_to_swu,
    swu_to_fsw,
    fsw_to_swu,
    symid_max,
    symid_min,
    symid_to_key,
    key_to_symid,
)


# ------------------------------------------------------------------ #
# 1. Marker ↔ SWU
# ------------------------------------------------------------------ #
@pytest.mark.parametrize(
    "swu,mark",
    [
        ("\U0001D800", "A"),
        ("\U0001D801", "B"),
        ("\U0001D802", "L"),
        ("\U0001D803", "M"),
        ("\U0001D804", "R"),
    ],
)
def test_swu_to_mark(swu, mark):
    assert swu_to_mark(swu) == mark
    assert swu_to_mark("x") == ""


@pytest.mark.parametrize(
    "mark,swu",
    [
        ("A", "\U0001D800"),
        ("B", "\U0001D801"),
        ("L", "\U0001D802"),
        ("M", "\U0001D803"),
        ("R", "\U0001D804"),
    ],
)
def test_mark_to_swu(mark, swu):
    assert mark_to_swu(mark) == swu
    assert mark_to_swu("x") == ""


# ------------------------------------------------------------------ #
# 2. Numbers & Coordinates
# ------------------------------------------------------------------ #
def test_swu_to_num_and_back():
    assert swu_to_num("𝤆") == 500
    assert num_to_swu(500) == "𝤆"
    assert num_to_swu(250) == "\U0001D80C"


def test_swu_to_coord_and_back():
    coord = swu_to_coord("𝤆𝤆")
    assert coord == [500, 500]
    assert coord_to_swu(coord) == "𝤆𝤆"


def test_fsw_to_coord_and_back():
    assert fsw_to_coord("500x500") == [500, 500]
    assert coord_to_fsw([500, 500]) == "500x500"
    assert fsw_to_coord("invalid") == []


# ------------------------------------------------------------------ #
# 3. Symbol ↔ Code ↔ ID ↔ Key
# ------------------------------------------------------------------ #
def test_swu_to_code_and_back():
    assert swu_to_code("\U00040012") == 0x40012
    assert code_to_swu(0x40012) == "\U00040012"


def test_swu_to_id_and_back():
    assert swu_to_id("\U00040012") == 18
    assert id_to_swu(18) == "\U00040012"


def test_key_to_id_and_back():
    assert key_to_id("S10000") == 1
    assert id_to_key(1) == "S10000"
    assert key_to_id("S00000") == 0
    assert id_to_key(0) == "S00000"


def test_swu_to_key_and_back():
    assert swu_to_key("\U00040012") == "S10011"
    assert key_to_swu("S10011") == "\U00040012"
    assert swu_to_key("\U00040000") == "S00000"
    assert key_to_swu("S00000") == "\U00040000"


# ------------------------------------------------------------------ #
# 4. Full-text conversion (needs regex patterns)
# ------------------------------------------------------------------ #
def test_swu_to_fsw_full():
    swu = "𝠀񀀒񀀚񋚥񋛩𝠃𝤟𝤩񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭"
    fsw = swu_to_fsw(swu)
    assert (
        fsw
        == "AS10011S10019S2e704S2e748M525x535S2e748483x510S10011501x466S2e704510x500S10019476x475"
    )


def test_fsw_to_swu_full():
    fsw = "AS10011S10019S2e704S2e748M525x535S2e748483x510S10011501x466S2e704510x500S10019476x475"
    swu = fsw_to_swu(fsw)
    assert swu == "𝠀񀀒񀀚񋚥񋛩𝠃𝤟𝤩񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭"


# ------------------------------------------------------------------ #
# 5. Symid helpers
# ------------------------------------------------------------------ #
@pytest.mark.parametrize(
    "min_id, max_id",
    [
        ("101011", "01-01-001-01"),
        ("101011616", "01-01-001-01-06-16"),
    ],
)
def test_symid_max(min_id, max_id):
    assert symid_max(min_id) == max_id
    assert symid_max("invalid") == ""


@pytest.mark.parametrize(
    "max_id, min_id",
    [
        ("01-01-001-01", "101011"),
        ("01-01-001-01-06-16", "101011616"),
    ],
)
def test_symid_min(max_id, min_id):
    assert symid_min(max_id) == min_id
    assert symid_min("bad") == ""


def test_symid_to_key():
    assert symid_to_key("01-01-001-01") == "S100"
    assert symid_to_key("01-01-001-01-06-16") == "S1005f"
    assert symid_to_key("bad") == ""


def test_key_to_symid():
    assert key_to_symid("S100") == "01-01-001-01"
    assert key_to_symid("S1005f") == "01-01-001-01-06-16"
    assert key_to_symid("S999") == ""  # out of range


# ------------------------------------------------------------------ #
# 6. Edge-case sanity checks (empty strings, None, etc.)
# ------------------------------------------------------------------ #
def test_empty_inputs():
    #    assert swu_to_fsw("") == ""
    #    assert fsw_to_swu("") == ""
    #    assert swu_to_key("") == ""
    #    assert key_to_swu("") == ""
    assert symid_max("") == ""
    assert symid_min("") == ""


if __name__ == "__main__":
    pytest.main(["-vv"])
