"""
The convert module contains functions to convert between Formal SignWriitng in ASCII (FSW) and SignWriting in Unicode (SWU) characters, along with other types of data.

Characters set definitions: https://datatracker.ietf.org/doc/id/draft-slevinski-formal-signwriting-10.html#name-character-sets
"""

from __future__ import annotations

import re
from typing import List, TypeVar, Optional, Union

from .symid_arr import symid_arr
from .regex import (
    fsw_pattern_prefix,
    fsw_pattern_box,
    fsw_pattern_coord,
    fsw_pattern_spatial,
    swu_pattern_null_or_symbol,
    swu_pattern_coord,
)


# ----------------------------
# Utility function
# ----------------------------

T = TypeVar("T")


def drop_none(d: dict[str, T | None]) -> dict[str, T]:
    """
    Remove key-value pairs from a dictionary where the value is None.

    Args:
        d: Input dictionary with optional values.

    Returns:
        Dictionary with same keys and non-None values.

    Example:
        >>> drop_none({"a": 1, "b": None, "c": "x"})
        {"a": 1, "c": "x"}
    """
    return {k: v for k, v in d.items() if v is not None}


def to_zoom(zoom: Optional[Union[int, float, str]]) -> float:
    """Convert zoom to float, handling 'x' and None."""
    if zoom == "x" or zoom is None:
        return 1.0
    return float(zoom)


# ----------------------------
# Convert functions
# ----------------------------


_SWU_TO_MARK: dict[str, str] = {
    "\U0001D800": "A",
    "\U0001D801": "B",
    "\U0001D802": "L",
    "\U0001D803": "M",
    "\U0001D804": "R",
}
_MARK_TO_SWU: dict[str, str] = {v: k for k, v in _SWU_TO_MARK.items()}


def swu_to_mark(swu_mark: str) -> str:
    """
    Convert an SWU structural marker to FSW equivalent.

    Args:
        swu_mark: single-character SWU marker

    Returns:
        single-letter FSW marker

    Example:
        >>> swu_to_mark('𝠀')
        'A'
    """
    return _SWU_TO_MARK.get(swu_mark, "")


def mark_to_swu(fsw_mark: str) -> str:
    """
    Convert an FSW structural marker to SWU equivalent.

    Args:
        fsw_mark: single-letter FSW marker

    Returns:
        single-character SWU marker

    Example:
        >>> mark_to_swu('A')
        '𝠀'
    """
    return _MARK_TO_SWU.get(fsw_mark, "")


def swu_to_num(swu_num: str) -> int:
    """
    Convert an SWU number character to an integer.

    Args:
        swu_num: a single SWU number character

    Returns:
        integer value

    Example:
        >>> swu_to_num('𝤆')
        500
    """
    return ord(swu_num) - 0x1D80C + 250


def num_to_swu(num: int) -> str:
    """
    Convert an integer to an SWU number character.

    Args:
        num: integer

    Returns:
        single SWU number character

    Example:
        >>> num_to_swu(500)
        '𝤆'
    """
    return chr(0x1D80C + int(num) - 250)


def swu_to_coord(swu_coord: str) -> List[int]:
    """
    Convert two SWU number characters to an [x, y] integer list.

    Args:
        swu_coord: string of two SWU number characters

    Returns:
        [x, y] integer list

    Example:
        >>> swu_to_coord('𝤆𝤆')
        [500, 500]
    """
    if len(swu_coord) != 2:
        return []
    return [swu_to_num(swu_coord[0]), swu_to_num(swu_coord[1])]


def coord_to_swu(coord: List[int]) -> str:
    """
    Convert an [x, y] integer list to two SWU number characters.

    Args:
        coord: [x, y] integer list

    Returns:
        string of two SWU number characters

    Example:
        >>> coord_to_swu([500, 500])
        '𝤆𝤆'
    """
    return "".join(num_to_swu(n) for n in coord)


def fsw_to_coord(fsw_coord: str) -> List[int]:
    """
    Convert an FSW coordinate string to [x, y] integer list.

    Args:
        fsw_coord: fsw coordinate string

    Returns:
        [x, y] integer list

    Example:
        >>> fsw_to_coord('500x500')
        [500, 500]
    """
    parts = fsw_coord.split("x")
    if len(parts) != 2:
        return []
    try:
        return [int(parts[0]), int(parts[1])]
    except ValueError:
        return []


def coord_to_fsw(coord: List[int]) -> str:
    """
    Convert an [x, y] list to an FSW coordinate string ('500x500').

    Args:
        coord: [x, y] integer list

    Returns:
        fsw coordinate string

    Example:
        >>> coord_to_fsw([500, 500])
        '500x500'
    """
    return "x".join(str(int(n)) for n in coord)


def swu_to_code(swu_sym: str) -> int:
    """
    Convert an SWU symbol character to its Unicode code point.

    Args:
        swu_sym: SWU symbol character

    Returns:
        integer codepoint

    Example:
        >>> swu_to_code('񀀁')
        0x40001
    """
    return ord(swu_sym)


def code_to_swu(code: int) -> str:
    """
    Convert a codepoint on plane 4 to an SWU symbol character.

    Args:
        code: integer codepoint

    Returns:
        SWU symbol character

    Example:
        >>> code_to_swu(0x40001)
        '񀀁'
    """
    return chr(int(code))


def swu_to_id(swu_sym: str) -> int:
    """
    Convert an SWU symbol character to a 16-bit ID.

    Args:
        swu_sym: SWU symbol character

    Returns:
        16-bit ID

    Example:
        >>> swu_to_id('񀀁')
        1
    """
    return swu_to_code(swu_sym) - 0x40000


def id_to_swu(id_: int) -> str:
    """
    Convert a 16-bit ID to an SWU symbol character.

    Args:
        id_: 16-bit ID

    Returns:
        SWU symbol character

    Example:
        >>> id_to_swu(1)
        '񀀁'
    """
    return code_to_swu(int(id_) + 0x40000)


def key_to_id(key: str) -> int:
    """
    Convert an FSW symbol key to a 16-bit ID.

    Args:
        key: FSW symbol key

    Returns:
        16-bit ID

    Example:
        >>> key_to_id('S10000')
        1
    """
    if key == "S00000":
        return 0
    base = int(key[1:4], 16)
    fill = int(key[4:5], 16)
    rot = int(key[5:6], 16)
    return 1 + ((base - 0x100) * 96) + (fill * 16) + rot


def id_to_key(id_: int) -> str:
    """
    Convert a 16-bit ID to an FSW symbol key.

    Args:
        id_: 16-bit ID

    Returns:
        FSW symbol key

    Example:
        >>> id_to_key(1)
        'S10000'
    """
    if int(id_) == 0:
        return "S00000"
    symcode = int(id_) - 1
    base = symcode // 96
    fill = (symcode - base * 96) // 16
    rot = symcode - base * 96 - fill * 16
    return f"S{base + 0x100:x}{fill:x}{rot:x}"


def swu_to_key(swu_sym: str) -> str:
    """
    Convert an SWU symbol character to an FSW symbol key.

    Args:
        swu_sym: SWU symbol character

    Returns:
        FSW symbol key

    Example:
        >>> swu_to_key('񀀁')
        'S10000'
    """
    if swu_sym == "\U00040000":
        return "S00000"
    symcode = swu_to_code(swu_sym) - 0x40001
    base = symcode // 96
    fill = (symcode - base * 96) // 16
    rot = symcode - base * 96 - fill * 16
    return f"S{base + 0x100:x}{fill:x}{rot:x}"


def key_to_swu(key: str) -> str:
    """
    Convert an FSW symbol key to an SWU symbol character.

    Args:
        key: FSW symbol key

    Returns:
        SWU symbol character

    Example:
        >>> key_to_swu('S10000)
        '񀀁'
    """
    if key == "S00000":
        return "\U00040000"
    base = int(key[1:4], 16)
    fill = int(key[4:5], 16)
    rot = int(key[5:6], 16)
    code = 0x40001 + ((base - 0x100) * 96) + (fill * 16) + rot
    return chr(code)


def swu_to_fsw(swu_text: str) -> str:
    """
    Convert SWU text to FSW text.

    Args:
        swu_text: SWU text string

    Returns:
        SWU text string

    Example:
        >>> swu_to_fsw('𝠀񀀒񀀚񋚥񋛩𝠃𝤟𝤩񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭')
        'AS10011S10019S2e704S2e748M525x535S2e748483x510S10011501x466S2e704510x500S10019476x475'
    """
    if not swu_text:
        return ""

    fsw = swu_text
    for swu_c, mark in _SWU_TO_MARK.items():
        fsw = fsw.replace(swu_c, mark)

    symbols = re.findall(swu_pattern_null_or_symbol, fsw)
    for sym in symbols:
        fsw = fsw.replace(sym, swu_to_key(sym), 1)

    coords = re.findall(swu_pattern_coord, fsw)
    for coord in coords:
        fsw = fsw.replace(coord, coord_to_fsw(swu_to_coord(coord)), 1)

    return fsw


def fsw_to_swu(fsw_text: str) -> str:
    """
    Convert FSW text to SWU text.

    Args:
        fsw_text: FSW text string

    Returns:
        SWU text string

    Example:
        >>> fsw_to_swu('AS10011S10019S2e704S2e748M525x535S2e748483x510S10011501x466S2e704510x500S10019476x475')
        '𝠀񀀒񀀚񋚥񋛩𝠃𝤟𝤩񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭'
    """
    if not fsw_text:
        return ""

    text = fsw_text

    prefixes = re.findall(fsw_pattern_prefix, text)
    for prefix in prefixes:
        keys = [prefix[i : i + 6] for i in range(1, len(prefix), 6)]
        swu_seq = "".join(key_to_swu(k) for k in keys)
        text = text.replace(prefix, "\U0001D800" + swu_seq, 1)

    box_coords = re.findall(fsw_pattern_box + fsw_pattern_coord, text)
    for box in box_coords:
        mark = box[0]
        coord_str = box[1:8]
        replacement = mark_to_swu(mark) + coord_to_swu(fsw_to_coord(coord_str))
        text = text.replace(box, replacement, 1)

    spatials = re.findall(fsw_pattern_spatial, text)
    for spatial in spatials:
        key = spatial[:6]
        coord_str = spatial[6:13]
        replacement = key_to_swu(key) + coord_to_swu(fsw_to_coord(coord_str))
        text = text.replace(spatial, replacement, 1)

    return text


def symid_max(symid_min: str) -> str:
    """
    Convert base or full symbol ID Min to symbol ID Max.

    Args:
        symid_min: minimized symbol ID

    Returns:
        maximized symbol ID

    Examples:
        >>> symid_max('101011')
        '01-01-001-01'
        >>> symid_max('101011616')
        '01-01-001-01-06-16'
    """
    if not re.fullmatch(r"\d{6}(\d{3})?", symid_min):
        return ""
    parts = [symid_min[i] for i in range(6)]
    max_str = f"0{parts[0]}-{parts[1]}{parts[2]}-0{parts[3]}{parts[4]}-0{parts[5]}"
    if len(symid_min) > 6:
        extra = [symid_min[i] for i in range(6, 9)]
        max_str += f"-0{extra[0]}-{extra[1]}{extra[2]}"
    return max_str


def symid_min(symid_max: str) -> str:
    """
    Convert base or full symbol ID Max to symbol ID Min.

    Args:
        symid_max: maximized symbol ID

    Returns:
        minimized symbol ID

    Examples:
        >>> symid_min('01-01-001-01')
        '101011'
        >>> symid_min('01-01-001-01-06-16')
        '101011616'
    """
    m = re.fullmatch(r"0(\d)-(\d{2})-0(\d{2})-0(\d)(?:-0(\d)-(\d{2}))?", symid_max)
    if not m:
        return ""
    base = m.group(1) + m.group(2) + m.group(3) + m.group(4)
    return base + (m.group(5) + m.group(6) if m.group(5) else "")


def symid_to_key(symid: str) -> str:
    """
    Convert base or full symbol ID max to FSW symbol key.

    Args:
        symid: base of full maximized symbol ID

    Returns:
        FSW symbol key

    Examples:
        >>> symid_to_key('01-01-001-01')
        'S100'
        >>> symid_to_key('01-01-001-01-06-16')
        'S1005f'
    """
    m = re.fullmatch(r"0(\d)-(\d{2})-0(\d{2})-0(\d)(?:-0(\d)-(\d{2}))?", symid)
    if not m:
        return ""
    base_min = m.group(1) + m.group(2) + m.group(3) + m.group(4)
    try:
        i = symid_arr.index(base_min)
    except ValueError:
        return ""

    if m.group(5):
        fill = int(m.group(5)) - 1
        rot = int(m.group(6)) - 1
        return f"S{256 + i:x}{fill}{rot:x}"
    else:
        return f"S{256 + i:x}"


def key_to_symid(key: str) -> str:
    """
    Convert base or full FSW symbol key to maximized symbol ID.

    Args:
        key: FSW symbol key

    Returns:
        maximized symbol ID

    Examples:
        >>> key_to_symid('S100')
        '01-01-001-01'
        >>> key_to_symid('S1005f')
        '01-01-001-01-06-16'
    """
    m = re.fullmatch(
        r"S([1-3][0-9a-f]{2})(?:([0-5])([0-9a-f]))?", key, flags=re.IGNORECASE
    )
    if not m:
        return ""
    i = int(m.group(1), 16) - 256
    if i >= len(symid_arr):
        return ""

    base = symid_max(symid_arr[i])
    if m.group(3):
        fill = 1 + int(m.group(2))
        rot = int(m.group(3), 16) + 1
        return f"{base}-0{fill}-{rot:02d}"
    return base


__all__ = [
    "drop_none",
    "to_zoom",
    "swu_to_mark",
    "mark_to_swu",
    "swu_to_num",
    "num_to_swu",
    "swu_to_coord",
    "coord_to_swu",
    "fsw_to_coord",
    "coord_to_fsw",
    "swu_to_code",
    "code_to_swu",
    "swu_to_id",
    "id_to_swu",
    "key_to_id",
    "id_to_key",
    "swu_to_key",
    "key_to_swu",
    "swu_to_fsw",
    "fsw_to_swu",
    "symid_max",
    "symid_min",
    "symid_to_key",
    "key_to_symid",
]
