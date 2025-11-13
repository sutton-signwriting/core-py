"""
The fswquery module contains functions for handling the FSW query language.

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

from .convert import fsw_to_coord, coord_to_fsw

from .regex import (
    style_pattern_full,
    fsw_pattern_prefix,
    fsw_pattern_signbox,
    fsw_pattern_null_or_symbol,
    fsw_pattern_symbol,
    fsw_pattern_coord,
    fswquery_pattern_var,
    fswquery_pattern_list,
    fswquery_pattern_item,
    fswquery_pattern_symbol,
    fswquery_pattern_range,
    fswquery_pattern_full,
    fswquery_pattern_coord,
    fswquery_pattern_null_or_symbol,
)

from .fsw import (
    fsw_parse_sign,
)


# ----------------------------
# FSW Query Parsing
# ----------------------------


def _fswquery_parse_prefix(text: str) -> QueryPrefix:
    if text == "T":
        return {"required": True}
    parts = re.findall(fswquery_pattern_list, text)
    processed_parts: List[QueryPrefixElement] = []
    for part in parts:
        if "o" in part:
            or_parts = re.findall(fswquery_pattern_item, part)
            processed = ["or_list"]
            for or_part in or_parts:
                if or_part.startswith("S"):
                    processed.append(or_part)
                else:
                    processed.append(or_part[1:].split("t"))
            processed_parts.append(processed)
        else:
            if part.startswith("S"):
                processed_parts.append(part)
            else:
                processed_parts.append(part[1:].split("t"))
    return {"required": True, "parts": processed_parts}


def _fswquery_parse_signbox(text: str) -> List[QuerySignboxElement]:
    """
    Parse a signbox query string into a list of query elements.

    Args:
        text: A string representing the signbox query.

    Returns:
        A list of QuerySignboxElement (symbols, ranges, or OR groups).
    """
    items = re.findall(rf"{fswquery_pattern_list}{fswquery_pattern_coord}", text)
    processed: List[QuerySignboxElement] = []

    for item in items:
        coord_str = item[-7:] if "x" in item[-7:] else ""
        front = item[:-7] if coord_str else item
        coord = fsw_to_coord(coord_str) if coord_str else None

        if "o" in front:
            or_parts = front.split("o")
            or_list: List[Union[str, List[str]]] = []
            for or_part in or_parts:
                if "S" in or_part:
                    or_list.append(or_part)
                else:
                    or_list.append(or_part[1:].split("t"))
            query_or: QuerySignboxOr = {"or_list": or_list}
            if coord is not None:
                query_or["coord"] = coord
            processed.append(query_or)
        elif "S" in front:
            query_symbol: QuerySignboxSymbol = {"symbol": front}
            if coord is not None:
                query_symbol["coord"] = coord
            processed.append(query_symbol)
        else:
            query_range: QuerySignboxRange = {"range": front[1:].split("t")}
            if coord is not None:
                query_range["coord"] = coord
            processed.append(query_range)

    return processed


def fswquery_parse(fsw_query_string: str) -> QueryObject:
    """
    Parse an FSW query string to a structured dictionary.

    Args:
        fsw_query_string: an FSW query string

    Returns:
        Dictionary representing the query structure

    Example:
        >>> fswquery_parse('QAS10000S10500oS20500oR2fft304TS100uuR205t206oS207uu510x510V5-')
        {'query': True,
         'prefix': {'required': True,
                    'parts': ['S10000',
                              ['or_list', 'S10500', 'S20500', ['2ff', '304']]]},
         'signbox': [{'symbol': 'S100uu'},
                     {'or_list': [['205', '206'], 'S207uu'], 'coord': [510, 510]}],
         'variance': 5,
         'style': True}
    """
    pattern = re.compile(rf"^{fswquery_pattern_full}$")
    m = pattern.match(fsw_query_string)
    if not m:
        return {"query": False}

    result: QueryObject = {"query": True}
    prefix = _fswquery_parse_prefix(m.group(1)) if m.group(1) else None
    if prefix is not None:
        result["prefix"] = prefix
    signbox = _fswquery_parse_signbox(m.group(2)) if m.group(2) else None
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
# FSW Query Compose
# ----------------------------


def fswquery_compose(fsw_query_object: QueryObject) -> Optional[str]:
    """
    Function to compose FSW query string from object.

    Args:
        fsw_query_object: Dictionary of type QueryObject

    Returns:
        FSW query string

    Example:
        >>> fswquery_compose({
        ...     'query': True,
        ...     'prefix': {
        ...         'required': True,
        ...         'parts': [
        ...             'S10000',
        ...             ['100', '204'],
        ...             'S20500'
        ...         ]
        ...     },
        ...     'signbox': [
        ...         {'symbol': 'S20000'},
        ...         {'range': ['100', '105'], 'coord': [500, 500]}
        ...     ],
        ...     'variance': 5,
        ...     'style': True
        ... })
        'QAS10000R100t204S20500TS20000R100t105500x500V5-'
    """
    if not fsw_query_object or not fsw_query_object.get("query"):
        return None

    query = "Q"

    prefix_obj = fsw_query_object.get("prefix")
    if prefix_obj and prefix_obj.get("required"):
        parts = prefix_obj.get("parts")
        if isinstance(parts, list):
            query += "A"
            for part in parts:
                if isinstance(part, str):
                    query += part
                elif isinstance(part, list) and len(part) == 2:
                    query += f"R{part[0]}t{part[1]}"
                elif isinstance(part, list) and len(part) > 2 and part[0] == "or_list":
                    or_parts = part[1:]
                    or_strs = []
                    for or_part in or_parts:
                        if isinstance(or_part, str):
                            or_strs.append(or_part)
                        elif isinstance(or_part, list) and len(or_part) == 2:
                            or_strs.append(f"R{or_part[0]}t{or_part[1]}")
                    query += "o".join(or_strs)
        query += "T"

    signbox = fsw_query_object.get("signbox")
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
                            or_strs.append(f"R{item[0]}t{item[1]}")
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
                    out = f"R{query_range['range'][0]}t{query_range['range'][1]}"

                coord = part_sb.get("coord")
                if isinstance(coord, list) and len(coord) == 2:
                    out += coord_to_fsw(coord)

            query += out

    variance = fsw_query_object.get("variance")
    if isinstance(variance, int):
        query += f"V{variance}"

    if fsw_query_object.get("style"):
        query += "-"

    match = re.match(f"^({fswquery_pattern_full})$", query)
    return match.group(1) if match else None


# ----------------------------
# FSW to Query
# ----------------------------


def fsw_to_query(fsw_sign: str, flags: str) -> Optional[str]:
    """
    Function to convert an FSW sign to a query string.

    For the flags parameter, use one or more of the following:
    - A: exact symbol in temporal prefix
    - a: general symbol in temporal prefix
    - S: exact symbol in spatial signbox
    - s: general symbol in spatial signbox
    - L: spatial signbox symbol at location

    Args:
        fsw_sign: FSW sign
        flags: flags for query string creation

    Returns:
        FSW query string

    Example:
        >>> fsw_to_query('AS10011S10019S2e704S2e748M525x535S2e748483x510S10011501x466S2e704510x500S10019476x475', 'ASL')
        'QAS10011S10019S2e704S2e748TS2e748483x510S10011501x466S2e704510x500S10019476x475'
    """
    query = ""
    parsed = fsw_parse_sign(fsw_sign)

    if not parsed.get("box"):
        return None

    A_flag = "A" in flags
    a_flag = "a" in flags
    S_flag = "S" in flags
    s_flag = "s" in flags
    L_flag = "L" in flags

    if A_flag or a_flag or S_flag or s_flag:
        if (A_flag or a_flag) and (sequence := parsed.get("sequence")):
            query += "A"
            query += "".join(
                sym[:4] + ("uu" if a_flag else sym[4:6]) for sym in sequence
            )
            query += "T"

        if (S_flag or s_flag) and (spatials := parsed.get("spatials")):
            for spatial in spatials:
                sym = spatial["symbol"]
                query += sym[:4] + ("uu" if s_flag else sym[4:6])
                if L_flag:
                    query += "x".join(map(str, spatial["coord"]))

    return "Q" + query if query else None


# ----------------------------
# FSW Query Range
# ----------------------------


def _range_pattern(low: str, high: str, is_hex: bool) -> str:
    if low == high:
        return low
    if not is_hex:
        return f"[{low}-{high}]"
    hex_digits = "0123456789abcdef"
    low_index = hex_digits.index(low)
    high_index = hex_digits.index(high)
    range_str = hex_digits[low_index : high_index + 1]
    numeric_match = re.search(r"[0-9]+", range_str)
    alpha_match = re.search(r"[a-f]+", range_str)
    numeric = numeric_match.group(0) if numeric_match else ""
    alpha = alpha_match.group(0) if alpha_match else ""
    if numeric and alpha:
        return f"[{numeric[0]}-{numeric[-1]}{alpha[0]}-{alpha[-1]}]"
    elif numeric:
        return f"[{numeric[0]}-{numeric[-1]}]"
    elif alpha:
        return f"[{alpha[0]}-{alpha[-1]}]"
    else:
        return ""


def _regex_geq(p: str, q: str, is_hex: bool) -> str:
    digit_seq = "0123456789abcdef" if is_hex else "0123456789"
    last_digit = digit_seq[-1]
    p_index = digit_seq.index(p)
    if q == digit_seq[0]:
        return _range_pattern(p, last_digit, is_hex) + (
            "[0-9a-f]" if is_hex else "[0-9]"
        )
    else:
        q_range = _range_pattern(q, last_digit, is_hex)
        next_p = digit_seq[p_index + 1] if p_index + 1 < len(digit_seq) else None
        if next_p:
            next_range = _range_pattern(next_p, last_digit, is_hex)
            return p + q_range + "|" + next_range + ("[0-9a-f]" if is_hex else "[0-9]")
        else:
            return p + q_range


def _regex_leq(r: str, s: str, is_hex: bool) -> str:
    digit_seq = "0123456789abcdef" if is_hex else "0123456789"
    first_digit = digit_seq[0]
    r_index = digit_seq.index(r)
    if r_index > 0:
        prev_r = digit_seq[r_index - 1]
        prev_part = (
            _range_pattern(first_digit, prev_r, is_hex)
            + ("[0-9a-f]" if is_hex else "[0-9]")
            + "|"
        )
        s_range = _range_pattern(first_digit, s, is_hex)
        return prev_part + r + s_range
    else:
        s_range = _range_pattern(first_digit, s, is_hex)
        return r + s_range


def _regex_between_two_digits(s: str, t: str, is_hex: bool) -> str:
    s1, s2 = s[0], s[1]
    t1, t2 = t[0], t[1]
    digit_seq = "0123456789abcdef" if is_hex else "0123456789"
    s1_index = digit_seq.index(s1)
    t1_index = digit_seq.index(t1)
    if s1_index < t1_index:
        parts = [f"{s1}{_range_pattern(s2, digit_seq[-1], is_hex)}"]
        middle_digits = digit_seq[s1_index + 1 : t1_index]
        if middle_digits:
            parts.append(
                _range_pattern(middle_digits[0], middle_digits[-1], is_hex)
                + ("[0-9a-f]" if is_hex else "[0-9]")
            )
        parts.append(f"{t1}{_range_pattern(digit_seq[0], t2, is_hex)}")
        return "|".join(parts)
    else:
        return f"{s1}{_range_pattern(s2, t2, is_hex)}"


def fswquery_range(
    min_: Union[int, str], max_: Union[int, str], hex_: bool = False
) -> str:
    """
    Function to transform a range to a regular expression.

    Args:
        min_: either a decimal number or hexidecimal string
        max_: either a decimal number or hexidecimal string
        hex_: if True, the regular expression will match a hexidecimal range

    Returns:
        a regular expression that matches a range

    Example:
        >>> fswquery_range(500, 750)
        '(([56][0-9][0-9])|(7[0-4][0-9])|(750))'
        >>> fswquery_range('100', '10e', True)
        '10[0-9a-e]'
    """
    if isinstance(min_, int):
        min_str = f"{min_:03d}"
    else:
        min_str = f"{min_:0>3}"

    if isinstance(max_, int):
        max_str = f"{max_:03d}"
    else:
        max_str = str(max_)

    a, b, c = min_str[0], min_str[1], min_str[2]
    d, e, f = max_str[0], max_str[1], max_str[2]

    digit_seq = "0123456789abcdef" if hex_ else "0123456789"
    a_index = digit_seq.index(a)
    d_index = digit_seq.index(d)
    if a_index > d_index:
        raise ValueError("Start is greater than end")

    if a == d:
        between_pattern = _regex_between_two_digits(b + c, e + f, hex_)
        return (
            f"{a}(?:{between_pattern})"
            if "|" in between_pattern
            else f"{a}{between_pattern}"
        )
    else:
        parts = []
        geq_pattern = _regex_geq(b, c, hex_)
        parts.append(
            f"{a}(?:{geq_pattern})" if "|" in geq_pattern else f"{a}{geq_pattern}"
        )

        if a_index + 1 < d_index:
            middle_digits = digit_seq[a_index + 1 : d_index]
            middle_pattern = _range_pattern(middle_digits[0], middle_digits[-1], hex_)
            digit_class = "[0-9a-f]" if hex_ else "[0-9]"
            parts.append(middle_pattern + digit_class + digit_class)

        leq_pattern = _regex_leq(e, f, hex_)
        parts.append(
            f"{d}(?:{leq_pattern})" if "|" in leq_pattern else f"{d}{leq_pattern}"
        )

        return f"(?:{'|'.join(parts)})"


# ----------------------------
# FSW Query Regex
# ----------------------------


def _regex_symbol(sym: str) -> str:
    segment = sym[:4]
    fill = sym[4:5]
    if fill == "u":
        segment += "[0-5]"
    else:
        segment += fill
    rot = sym[5:6]
    if rot == "u":
        segment += "[0-9a-f]"
    else:
        segment += rot
    return segment


def _regex_range(sym_range: str) -> str:
    from_ = sym_range[1:4]
    to_ = sym_range[5:8]
    return "S" + fswquery_range(from_, to_, hex_=True) + "[0-5][0-9a-f]"


def fswquery_regex(query: str) -> List[str]:
    """
    Function to transform an FSW query string to one or more regular expressions.

    Args:
        query: an FSW query string

    Returns:
        a list of one or more regular expression strings

    Example:
        >>> fswquery_regex('QS100uuS20500480x520')
        ['(?:A(?:S[123][0-9a-f]{2}[0-5][0-9a-f])+)?[BLMR][0-9]{3}x[0-9]{3}(?:S[123][0-9a-f]{2}[0-5][0-9a-f][0-9]{3}x[0-9]{3})*S100[0-5][0-9a-f][0-9]{3}x[0-9]{3}(?:S[123][0-9a-f]{2}[0-5][0-9a-f][0-9]{3}x[0-9]{3})*',
         '(?:A(?:S[123][0-9a-f]{2}[0-5][0-9a-f])+)?[BLMR][0-9]{3}x[0-9]{3}(?:S[123][0-9a-f]{2}[0-5][0-9a-f][0-9]{3}x[0-9]{3})*S20500(?:4[6-9][0-9]|500)x(?:5[0-3][0-9]|540)(?:S[123][0-9a-f]{2}[0-5][0-9a-f][0-9]{3}x[0-9]{3})*']
    """
    pattern = re.compile(rf"^{fswquery_pattern_full}$")
    m = pattern.match(query)
    if not m:
        return []
    query = m.group(0)

    q_style = f"(?:{style_pattern_full})?"

    if query == "Q":
        return [f"{fsw_pattern_prefix}?{fsw_pattern_signbox}"]
    if query == "Q-":
        return [f"{fsw_pattern_prefix}?{fsw_pattern_signbox}{q_style}"]
    if query == "QT":
        return [f"{fsw_pattern_prefix}{fsw_pattern_signbox}"]
    if query == "QT-":
        return [f"{fsw_pattern_prefix}{fsw_pattern_signbox}{q_style}"]

    segments = []
    sortable = query.find("T") + 1
    q_sortable = ""
    if sortable:
        q_sortable = "(?:A"
        qat = query[:sortable]
        query = query[sortable:]
        if qat == "QT":
            q_sortable += f"{fsw_pattern_null_or_symbol}+)"
        else:
            matches = re.findall(fswquery_pattern_list, qat)
            if matches:
                for part in matches:
                    or_list = []
                    matches_or = re.findall(fswquery_pattern_item, part)
                    if matches_or:
                        for mor in matches_or:
                            matched = re.match(
                                rf"^{fswquery_pattern_null_or_symbol}$", mor
                            )
                            if matched:
                                or_list.append(_regex_symbol(matched.group(0)))
                            else:
                                or_list.append(_regex_range(mor))
                    if len(or_list) == 1:
                        q_sortable += or_list[0]
                    else:
                        q_sortable += f"(?:{'|'.join(or_list)})"
                q_sortable += f"{fsw_pattern_null_or_symbol}*)"

    fuzz = 20
    matches_var = re.search(fswquery_pattern_var, query)
    if matches_var:
        fuzz = int(matches_var.group(0)[1:])

    item_pattern = re.compile(rf"{fswquery_pattern_symbol}|{fswquery_pattern_range}")
    matches = re.findall(rf"{fswquery_pattern_list}{fswquery_pattern_coord}", query)
    if matches:
        for item in matches:
            or_list = []
            matches_or = item_pattern.findall(item)
            for mor in matches_or:
                if re.match(rf"^{fswquery_pattern_symbol}$", mor):
                    or_list.append(_regex_symbol(mor))
                else:
                    or_list.append(_regex_range(mor))
            if len(or_list) == 1:
                segment = or_list[0]
            else:
                segment = f"(?:{'|'.join(or_list)})"

            if "x" in item[-7:]:
                coord_str = item[-7:]
                coord = fsw_to_coord(coord_str)
                x, y = coord
                segment += fswquery_range(x - fuzz, x + fuzz)
                segment += "x"
                segment += fswquery_range(y - fuzz, y + fuzz)
            else:
                segment += fsw_pattern_coord

            segment = f"{fsw_pattern_signbox}{segment}(?:{fsw_pattern_symbol}{fsw_pattern_coord})*"
            if sortable:
                segment = q_sortable + segment
            else:
                segment = f"{fsw_pattern_prefix}?{segment}"
            if "-" in query:
                segment += q_style
            segments.append(segment)

    if not segments:
        segment = q_sortable + fsw_pattern_signbox
        if "-" in query:
            segment += q_style
        segments.append(segment)

    return segments


# ----------------------------
# FSW Query Results
# ----------------------------


def fswquery_results(query: str, text: str) -> List[str]:
    """
    Function that uses a query string to match signs from a string of text.

    Args:
        query: an FSW query string
        text: a string of text containing multiple signs

    Returns:
        an array of FSW signs

    Example:
        >>> fswquery_results('QAS10011T','AS10011S10019S2e704S2e748M525x535S2e748483x510S10011501x466S2e704510x500S10019476x475 AS15a21S15a07S21100S2df04S2df14M521x538S15a07494x488S15a21498x489S2df04498x517S2df14497x461S21100479x486 AS1f010S10018S20600M519x524S10018485x494S1f010490x494S20600481x476')
        ['AS10011S10019S2e704S2e748M525x535S2e748483x510S10011501x466S2e704510x500S10019476x475']
    """
    if not text:
        return []

    re_patterns = fswquery_regex(query)
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


def fswquery_lines(query: str, text: str) -> List[str]:
    """
    Function that uses an FSW query string to match signs from multiple lines of text.

    Args:
        query: an FSW query string
        text: multiple lines of text, each starting with an FSW sign

    Returns:
        an array of lines of text, each starting with an FSW sign

    Example:
        >>> fswquery_lines('QAS10011T',`AS10011S10019S2e704S2e748M525x535S2e748483x510S10011501x466S2e704510x500S10019476x475 line one
        ... AS15a21S15a07S21100S2df04S2df14M521x538S15a07494x488S15a21498x489S2df04498x517S2df14497x461S21100479x486 line two
        ... AS1f010S10018S20600M519x524S10018485x494S1f010490x494S20600481x476 line three`)
        ['AS10011S10019S2e704S2e748M525x535S2e748483x510S10011501x466S2e704510x500S10019476x475 line one']
    """
    if not text:
        return []

    re_patterns = fswquery_regex(query)
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
    "fswquery_parse",
    "fswquery_compose",
    "fsw_to_query",
    "fswquery_range",
    "fswquery_regex",
    "fswquery_results",
    "fswquery_lines",
]
