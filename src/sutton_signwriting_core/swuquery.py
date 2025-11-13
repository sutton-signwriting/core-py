"""
The swuquery module contains functions for handling the SWU query language.

Query Language definition: https://datatracker.ietf.org/doc/id/draft-slevinski-formal-signwriting-10.html#name-query-language
"""

import re
from typing import List, Optional, Union, cast

from .datatypes import (
    QueryObject,
    QueryPrefixElement,
    QueryPrefix,
    QuerySignboxElement,
    QuerySignboxOr,
    QuerySignboxRange,
    QuerySignboxSymbol,
)

from .convert import (
    swu_to_coord,
    coord_to_swu,
    num_to_swu,
    swu_to_key,
    key_to_swu,
)

from .regex import (
    style_pattern_full,
    swu_pattern_sort,
    swu_pattern_prefix,
    swu_pattern_box,
    swu_pattern_coord,
    swu_pattern_symbol,
    swu_pattern_null_or_symbol,
    swu_pattern_signbox,
    swuquery_pattern_coord,
    swuquery_pattern_var,
    swuquery_pattern_list,
    swuquery_pattern_item,
    swuquery_pattern_range,
    swuquery_pattern_symbol,
    swuquery_pattern_full,
)

from .swu import swu_parse_sign


# ----------------------------
# SWU Query Parsing
# ----------------------------


def _swuquery_parse_prefix(text: str) -> QueryPrefix:
    if text == "T":
        return {"required": True}
    parts = re.findall(swuquery_pattern_list, text)
    processed_parts: List[QueryPrefixElement] = []
    for part in parts:
        if "o" in part:
            or_parts = re.findall(swuquery_pattern_item, part)
            processed: list[Union[str, list[str]]] = ["or_list"]
            for or_part in or_parts:
                if or_part[0] != "R":
                    processed.append(or_part)
                else:
                    processed.append([or_part[1], or_part[2]])
            processed_parts.append(processed)
        else:
            if part[0] != "R":
                processed_parts.append(part)
            else:
                processed_parts.append([part[1], part[2]])
    return {"required": True, "parts": processed_parts}


def _swuquery_parse_signbox(text: str) -> List[QuerySignboxElement]:
    """
    Parse a signbox query string into a list of query elements.

    Args:
        text: A string representing the signbox query.

    Returns:
        A list of QuerySignboxElement (symbols, ranges, or OR groups).
    """
    items = re.findall(rf"{swuquery_pattern_list}{swuquery_pattern_coord}", text)
    processed: List[QuerySignboxElement] = []

    for item in items:
        coord_match = re.search(rf"{swuquery_pattern_coord}$", item)
        coord_str = coord_match.group(0) if coord_match else ""
        front = item[: -len(coord_str)] if coord_str else item
        coord = swu_to_coord(coord_str) if coord_str else None

        if "o" in front:
            or_parts = front.split("o")
            or_list = []
            for or_part in or_parts:
                if "R" not in or_part:
                    or_list.append(or_part)
                else:
                    or_list.append([or_part[1], or_part[2]])
            query_or: QuerySignboxOr = {"or_list": or_list}
            if coord is not None:
                query_or["coord"] = coord
            processed.append(query_or)
        elif "R" not in front:
            query_symbol: QuerySignboxSymbol = {"symbol": front}
            if coord is not None:
                query_symbol["coord"] = coord
            processed.append(query_symbol)
        else:
            query_range: QuerySignboxRange = {"range": [front[1], front[2]]}
            if coord is not None:
                query_range["coord"] = coord
            processed.append(query_range)

    return processed


def swuquery_parse(swu_query_string: str) -> QueryObject:
    """
    Parse an SWU query string to a structured dictionary.

    Args:
        swu_query_string: an SWU query string

    Returns:
        Dictionary representing the query structure

    Example:
        >>> swuquery_parse('QA񀀁R񀀁񆆑񆇡T񆀁R񀀁񀇱𝤆𝤆V5-')
        {'query': True,
         'prefix': {'required': True,
                    'parts': ['񀀁', ['񀀁', '񆆑'], '񆇡']},
         'signbox': [{'symbol': '񆀁'},
                     {'range': ['񀀁', '񀇱'], 'coord': [500, 500]}],
         'variance': 5,
         'style': True}
    """
    pattern = re.compile(rf"^{swuquery_pattern_full}$")
    m = pattern.match(swu_query_string)
    if not m:
        return {"query": False}

    result: QueryObject = {"query": True}
    prefix = _swuquery_parse_prefix(m.group(1)) if m.group(1) else None
    if prefix is not None:
        result["prefix"] = prefix
    signbox = _swuquery_parse_signbox(m.group(2)) if m.group(2) else None
    if signbox is not None:
        result["signbox"] = signbox
    variance = int(m.group(3)[1:]) if m.group(3) else None
    if variance is not None:
        result["variance"] = variance
    style = True if m.group(4) else None
    if style is not None:
        result["style"] = style

    return result


# ----------------------------
# SWU Query Compose
# ----------------------------


def swuquery_compose(swu_query_object: QueryObject) -> Optional[str]:
    """
    Function to compose SWU query string from object.

    Args:
        swu_query_object: Dictionary of type QueryObject

    Returns:
        SWU query string

    Example:
        >>> swuquery_compose({
        ...     'query': True,
        ...     'prefix': {
        ...         'required': True,
        ...         'parts': [
        ...             '񀀁',
        ...             ['񀀁', '񆆑'],
        ...             '񆇡'
        ...         ]
        ...     },
        ...     'signbox': [
        ...         {'symbol': '񆀁'},
        ...         {'range': ['񀀁', '񀇱'], 'coord': [500, 500]}
        ...     ],
        ...     'variance': 5,
        ...     'style': True
        ... })
        'QA񀀁R񀀁񆆑񆇡T񆀁R񀀁񀇱𝤆𝤆V5-'
    """
    if not swu_query_object or not swu_query_object.get("query"):
        return None

    query = "Q"

    prefix_obj = swu_query_object.get("prefix")
    if prefix_obj and prefix_obj.get("required"):
        parts = prefix_obj.get("parts")
        if isinstance(parts, list):
            query += "A"
            for part in parts:
                if isinstance(part, str):
                    query += part
                elif isinstance(part, list) and len(part) == 2:
                    query += f"R{part[0]}{part[1]}"
                elif isinstance(part, list) and len(part) > 2 and part[0] == "or_list":
                    or_parts = part[1:]
                    or_strs = []
                    for or_part in or_parts:
                        if isinstance(or_part, str):
                            or_strs.append(or_part)
                        elif isinstance(or_part, list) and len(or_part) == 2:
                            or_strs.append(f"R{or_part[0]}{or_part[1]}")
                    query += "o".join(or_strs)
        query += "T"

    signbox = swu_query_object.get("signbox")
    if isinstance(signbox, list):
        for part_sb in signbox:
            out = ""
            if isinstance(part_sb, dict):
                if "or_list" in part_sb:
                    query_or = cast(QuerySignboxOr, part_sb)
                    or_list: List[Union[str, List[str]]] = query_or["or_list"]
                    or_strs = []
                    for item in or_list:
                        if isinstance(item, str):
                            or_strs.append(item)
                        elif isinstance(item, list) and len(item) == 2:
                            or_strs.append(f"R{item[0]}{item[1]}")
                    out = "o".join(or_strs)
                elif "symbol" in part_sb:
                    query_symbol = cast(QuerySignboxSymbol, part_sb)
                    out = query_symbol["symbol"]
                elif (
                    "range" in part_sb
                    and isinstance(part_sb["range"], list)
                    and len(part_sb["range"]) == 2
                ):  # QuerySignboxRange
                    query_range = part_sb
                    out = f"R{query_range['range'][0]}{query_range['range'][1]}"

                coord = part_sb.get("coord")
                if isinstance(coord, list) and len(coord) == 2:
                    out += coord_to_swu(coord)

            query += out

    variance = swu_query_object.get("variance")
    if isinstance(variance, int):
        query += f"V{variance}"

    if swu_query_object.get("style"):
        query += "-"

    match = re.match(f"^({swuquery_pattern_full})$", query)
    return match.group(1) if match else None


# ----------------------------
# SWU to Query
# ----------------------------


def swu_to_query(swu_sign: str, flags: str) -> Optional[str]:
    """
    Function to convert an SWU sign to a query string.

    For the flags parameter, use one or more of the following:
    - A: exact symbol in temporal prefix
    - a: general symbol in temporal prefix
    - S: exact symbol in spatial signbox
    - s: general symbol in spatial signbox
    - L: spatial signbox symbol at location

    Args:
        swu_sign: SWU sign
        flags: flags for query string creation

    Returns:
        SWU query string

    Example:
        >>> swu_to_query('𝠀񀀒񀀚񋚥񋛩𝠃𝤟𝤩񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭', 'ASL')
        'QA񀀒񀀚񋚥񋛩T񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭'
    """
    parsed = swu_parse_sign(swu_sign)
    if not parsed.get("box"):
        return None

    a_flag = "A" in flags
    a_gen_flag = "a" in flags
    s_flag = "S" in flags
    s_gen_flag = "s" in flags
    l_flag = "L" in flags

    query = ""
    if (a_flag or a_gen_flag) and "sequence" in parsed:
        query += "A"
        for sym in parsed["sequence"]:
            query += sym + ("fr" if a_gen_flag else "")
        query += "T"

    if (s_flag or s_gen_flag) and "spatials" in parsed:
        for spatial in parsed["spatials"]:
            spatial_sym = spatial["symbol"]
            query += spatial_sym + ("fr" if s_gen_flag else "")
            if l_flag:
                query += coord_to_swu(spatial["coord"])

    return "Q" + query if query else None


# ------------------------------------------------------------------ #
# SWU Query Range
# ------------------------------------------------------------------ #


def swuquery_range(min_char: str, max_char: str) -> str:
    """
    Function to transform a range of SWU characters to a regular expression.

    Args:
        min_char: an SWU character
        max_char: an SWU character

    Returns:
        a regular expression that matches a range of SWU characters

    Example:
        >>> swuquery_range('񀀁', '񀇡')
        '[\\U00040001-\\U000401E1]'

        >>> swuquery_range('𝣔', '𝤸')
        '[\\U0001D8D4-\\U0001D938]'
    """
    if not (isinstance(min_char, str) and isinstance(max_char, str)):
        return ""
    if len(min_char) != 1 or len(max_char) != 1:
        return ""
    min_code = ord(min_char)
    max_code = ord(max_char)
    if min_code > max_code:
        return ""
    return f"[\\U{min_code:08X}-\\U{max_code:08X}]"


# ------------------------------------------------------------------ #
# SWU Query Regex
# ------------------------------------------------------------------ #


def _regex_range(sym_range: str) -> str:
    """
    Convert an SWU range (e.g., 'R񀀁񀇡') to a regex pattern.
    """
    from_key = swu_to_key(sym_range[1:2])
    to_key = swu_to_key(sym_range[-1:])
    from_char = key_to_swu(from_key[:4] + "00")
    to_char = key_to_swu(to_key[:4] + "5f")
    return swuquery_range(from_char, to_char)


def _regex_symbol(sym: str) -> str:
    """
    Convert an SWU symbol (possibly followed by 'f', 'r', or 'fr')
    into a regex covering all matching fills and/or rotations.

    Rules:
      - No suffix: match exactly this symbol
      - 'r': any rotation (same fill)
      - 'f': any fill (same rotation)
      - 'fr' or 'rf': any fill and rotation (full 96-symbol block)

    Examples:
        symbol_ranges("񀀁")   -> exact
        symbol_ranges("񀀁r")  -> contiguous 16 symbols
        symbol_ranges("񀀑f")  -> same rotation, all fills
        symbol_ranges("񀀑fr") -> all fills & rotations
    """
    base_char = sym[0]
    suffix = sym[1:] if len(sym) > 1 else ""
    base_code = ord(base_char)

    # Normalize to base symbol (fill=0, rotation=0)
    # Determine base by clearing fill/rotation offsets within the 96-symbol block.
    # Each symbol block starts every 0x60 codepoints.
    base_block = (base_code - 0x40001) // 0x60  # which symbol group
    base_start = 0x40001 + base_block * 0x60

    # Compute current offset within that block
    offset = base_code - base_start
    fill_index = offset // 0x10  # 0–5
    rot_index = offset % 0x10  # 0–15

    # total sizes
    rotation_block = 0x10
    total_block = 0x60  # 6 fills * 16 rotations = 96

    if suffix == "":
        # exact match only
        return f"\\U{base_code:08X}"

    elif suffix == "r":
        # same fill, any rotation → contiguous block of 16
        start = base_start + fill_index * rotation_block
        end = start + 0x0F
        return f"[\\U{start:08X}-\\U{end:08X}]"

    elif suffix == "f":
        # same rotation, any fill → six codepoints spaced by 0x10
        parts = [
            f"\\U{(base_start + rot_index + i * rotation_block):08X}" for i in range(6)
        ]
        return f"(?:{'|'.join(parts)})"

    elif suffix in ("fr", "rf"):
        # any fill, any rotation → contiguous 96-symbol block
        start = base_start
        end = base_start + total_block - 1
        return f"[\\U{start:08X}-\\U{end:08X}]"

    else:
        raise ValueError(f"Invalid suffix for SWU symbol: {sym}")


def swuquery_regex(query: str) -> List[str]:
    """
    Function to transform an SWU query string to one or more regular expressions.

    Args:
        query: an SWU query string

    Returns:
        a list of one or more regular expression strings

    Example:
        >>> swuquery_regex('QA񀀒T')
        ['(?:\\U0001d800\\U00040012(?:\\U00040000|(?:[\\U00040001-\\U0004f480]))*)\\U0001d80[1-4](?:\\U0001d8[0c-f][0-9a-f]|\\U0001d9[0-9a-f][0-9a-f]){2}(?:(?:[\\U00040001-\\U0004f480])(?:\\U0001d8[0c-f][0-9a-f]|\\U0001d9[0-9a-f][0-9a-f]){2})*']
    """
    pattern = re.compile(rf"^{swuquery_pattern_full}$")
    m = pattern.match(query)
    if not m:
        return []
    query = m.group(0)

    q_style = f"(?:{style_pattern_full})?"

    if query == "Q":
        return [
            f"{swu_pattern_prefix}?{swu_pattern_box}{swu_pattern_coord}(?:{swu_pattern_symbol}{swu_pattern_coord})*"
        ]
    if query == "Q-":
        return [
            f"{swu_pattern_prefix}?{swu_pattern_box}{swu_pattern_coord}(?:{swu_pattern_symbol}{swu_pattern_coord})*(?:{style_pattern_full})?"
        ]
    if query == "QT":
        return [
            f"{swu_pattern_prefix}{swu_pattern_box}{swu_pattern_coord}(?:{swu_pattern_symbol}{swu_pattern_coord})*"
        ]
    if query == "QT-":
        return [
            f"{swu_pattern_prefix}{swu_pattern_box}{swu_pattern_coord}(?:{swu_pattern_symbol}{swu_pattern_coord})*(?:{style_pattern_full})?"
        ]

    segments = []
    sortable = query.find("T") + 1
    q_sortable = ""
    if sortable:
        q_sortable = f"{swu_pattern_sort}"
        qat = query[:sortable]
        query = query[sortable:]
        if qat == "QT":
            q_sortable += f"{swu_pattern_null_or_symbol}+)"
        else:
            matches = re.findall(swuquery_pattern_list, qat)
            if matches:
                for part in matches:
                    or_list = []
                    matches_or = re.findall(swuquery_pattern_item, part)
                    if matches_or:
                        for mor in matches_or:
                            if re.match(rf"^{swuquery_pattern_range}$", mor):
                                or_list.append(_regex_range(mor))
                            else:
                                or_list.append(_regex_symbol(mor))
                    if len(or_list) == 1:
                        q_sortable += or_list[0]
                    else:
                        q_sortable += f"(?:{'|'.join(or_list)})"
                q_sortable += f"{swu_pattern_null_or_symbol}*"

    fuzz = 20
    matches_var = re.search(swuquery_pattern_var, query)
    if matches_var:
        fuzz = int(matches_var.group(0)[1:])

    item_pattern = re.compile(rf"{swuquery_pattern_symbol}|{swuquery_pattern_range}")
    matches = re.findall(rf"{swuquery_pattern_list}{swuquery_pattern_coord}", query)
    if matches:
        for item in matches:
            or_list = []
            matches_or = item_pattern.findall(item)
            for mor in matches_or:
                if re.match(rf"^{swuquery_pattern_range}$", mor):
                    or_list.append(_regex_range(mor))
                else:
                    or_list.append(_regex_symbol(mor))
            if len(or_list) == 1:
                segment = or_list[0]
            else:
                segment = f"(?:{'|'.join(or_list)})"

            coord_match = re.search(rf"{swuquery_pattern_coord}$", item)
            if coord_match and coord_match.group(0):
                coord = swu_to_coord(coord_match.group(0))
                x, y = coord
                segment += swuquery_range(num_to_swu(x - fuzz), num_to_swu(x + fuzz))
                segment += swuquery_range(num_to_swu(y - fuzz), num_to_swu(y + fuzz))
            else:
                segment += swu_pattern_coord

            segment = f"{swu_pattern_signbox}{segment}(?:{swu_pattern_symbol}{swu_pattern_coord})*"
            if sortable:
                segment = q_sortable + segment
            else:
                segment = f"{swu_pattern_prefix}?{segment}"
            if "-" in query:
                segment += q_style
            segments.append(segment)

    if not segments:
        segment = q_sortable + swu_pattern_signbox
        if "-" in query:
            segment += q_style
        segments.append(segment)

    return segments


def swuquery_results(query: str, text: str) -> List[str]:
    """
    Function that uses a query string to match signs from a string of text.

    Args:
        query: an SWU query string
        text: a string of text containing multiple signs

    Returns:
        an array of SWU signs

    Example:
        >>> swuquery_results('QA񀀒T','𝠀񀀒񀀚񋚥񋛩𝠃𝤟𝤩񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭 𝠀񂇢񂇈񆙡񋎥񋎵𝠃𝤛𝤬񂇈𝤀𝣺񂇢𝤄𝣻񋎥𝤄𝤗񋎵𝤃𝣟񆙡𝣱𝣸 𝠀񅨑񀀙񆉁𝠃𝤙𝤞񀀙𝣷𝤀񅨑𝣼𝤀񆉁𝣳𝣮')
        ['𝠀񀀒񀀚񋚥񋛩𝠃𝤟𝤩񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭']
    """
    if not text:
        return []

    re_patterns = swuquery_regex(query)
    if not re_patterns:
        return []

    for pattern in re_patterns:
        matches = re.findall(pattern, text)
        if matches:
            text = " ".join(matches)
        else:
            text = ""
            break  # No need to continue if no matches

    if text:
        words = list(dict.fromkeys(text.split(" ")))  # Dedup preserving order
        return [w for w in words if w]  # Filter empty
    return []


def swuquery_lines(query: str, text: str) -> List[str]:
    """
    Function that uses an SWU query string to match signs from multiple lines of text.

    Args:
        query: an SWU query string
        text: multiple lines of text, each starting with an SWU sign

    Returns:
        an array of lines of text, each starting with an SWU sign

    Example:
        >>> swuquery_lines('QA񀀒T', '''𝠀񀀒񀀚񋚥񋛩𝠃𝤟𝤩񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭 line one
        ... 𝠀񂇢񂇈񆙡񋎥񋎵𝠃𝤛𝤬񂇈𝤀𝣺񂇢𝤄𝣻񋎥𝤄𝤗񋎵𝤃𝣟񆙡𝣱𝣸 line two
        ... 𝠀񅨑񀀙񆉁𝠃𝤙𝤞񀀙𝣷𝤀񅨑𝣼𝤀񆉁𝣳𝣮 line three''')
        ['𝠀񀀒񀀚񋚥񋛩𝠃𝤟𝤩񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭 line one']
    """
    if not text:
        return []

    re_patterns = swuquery_regex(query)
    if not re_patterns:
        return []

    for pattern in re_patterns:
        pattern_with_anchor = f"^{pattern}.*"
        matches = re.findall(pattern_with_anchor, text, re.MULTILINE)
        if matches:
            text = "\n".join(matches)
        else:
            text = ""
            break  # No need to continue if no matches

    if text:
        lines_list = text.split("\n")
        unique_lines = list(dict.fromkeys(lines_list))  # Dedup preserving order
        return [line for line in unique_lines if line]  # Filter empty
    return []


__all__ = [
    "swuquery_parse",
    "swuquery_compose",
    "swu_to_query",
    "swuquery_range",
    "swuquery_regex",
    "swuquery_results",
    "swuquery_lines",
]
