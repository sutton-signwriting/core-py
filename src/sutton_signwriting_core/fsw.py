"""
The fsw module contains functions for handling Formal SignWriting in ASCII (FSW) characters.

FSW characters definition: https://datatracker.ietf.org/doc/id/draft-slevinski-formal-signwriting-10.html#name-formal-signwriting-in-ascii
"""

import re
from typing import Dict, List, Optional, Tuple, Union, Set, cast
from dataclasses import dataclass

from .datatypes import (
    SymbolObject,
    SignObject,
    SegmentInfo,
    ColumnOptions,
    ColumnSegment,
    ColumnsResult,
    SpecialToken,
    TokenizerMappings,
)

from .convert import drop_none, to_zoom, fsw_to_coord

from .regex import (
    fsw_pattern_box,
    fsw_pattern_coord,
    fsw_pattern_null_or_symbol,
    fsw_pattern_prefix,
    fsw_pattern_signbox,
    fsw_pattern_spatial,
    fsw_pattern_symbol,
    style_pattern_full,
)

from .style import (
    style_parse,
)

# ----------------------------
# FSW structure constants
# ----------------------------
# Names converted to fsw_structure_*

# kinds: writing, location, punctuation (numbers are the same as JS)
fsw_structure_kind: List[int] = [0x100, 0x37F, 0x387]

# categories: hand, movement, dynamics, head, trunk & limb, location, punctuation.
fsw_structure_category: List[int] = [0x100, 0x205, 0x2F7, 0x2FF, 0x36D, 0x37F, 0x387]

# the 30 symbol groups
fsw_structure_group: List[int] = [
    0x100,
    0x10E,
    0x11E,
    0x144,
    0x14C,
    0x186,
    0x1A4,
    0x1BA,
    0x1CD,
    0x1F5,
    0x205,
    0x216,
    0x22A,
    0x255,
    0x265,
    0x288,
    0x2A6,
    0x2B7,
    0x2D5,
    0x2E3,
    0x2F7,
    0x2FF,
    0x30A,
    0x32A,
    0x33B,
    0x359,
    0x36D,
    0x376,
    0x37F,
    0x387,
]

# ranges: mapping from names to start/end inclusive (same semantics as JS)
fsw_structure_ranges: Dict[str, Tuple[int, int]] = {
    "all": (0x100, 0x38B),
    "writing": (0x100, 0x37E),
    "hand": (0x100, 0x204),
    "movement": (0x205, 0x2F6),
    "dynamic": (0x2F7, 0x2FE),
    "head": (0x2FF, 0x36C),
    "hcenter": (0x2FF, 0x36C),
    "vcenter": (0x2FF, 0x375),
    "trunk": (0x36D, 0x375),
    "limb": (0x376, 0x37E),
    "location": (0x37F, 0x386),
    "punctuation": (0x387, 0x38B),
}


def fsw_is_type(sym_key: str, type_name: str) -> bool:
    """
    Test whether an FSW symbol key is of the given type/range.

    Args:
        sym_key: an FSW symbol key
        type_name: the name of a symbol range

    Returns:
        True if symbol of specified type

    Example:
        >>> fsw_is_type('S10000', 'hand')
        True

    Note:
        The following `type_name` values are supported:

        - **all** - All symbols used in Formal SignWriting.
        - **writing** - Symbols that can be used in the spatial signbox or the temporal prefix.
        - **hand** - Various handshapes.
        - **movement** - Contact symbols, small finger movements, straight arrows, curved arrows, and circles.
        - **dynamic** - Dynamic symbols used to express "feeling" or "tempo" of movement.
        - **head** - Symbols for the head and face.
        - **hcenter** - Used to determine the horizontal center of a sign (same as the head type).
        - **vcenter** - Used to determine the vertical center of a sign (includes head and trunk types).
        - **trunk** - Symbols for torso movement, shoulders, and hips.
        - **limb** - Symbols for limbs and fingers.
        - **location** - Detailed location symbols used only in the temporal prefix.
        - **punctuation** - Symbols used to divide signs into sentences.
    """
    if not (isinstance(sym_key, str) and sym_key.startswith("S") and len(sym_key) >= 4):
        return False
    # the group id is hex in positions 1..3 (slice [1:4])
    try:
        dec = int(sym_key[1:4], 16)
    except ValueError:
        return False
    rng = fsw_structure_ranges.get(type_name)
    if not rng:
        return False
    return rng[0] <= dec <= rng[1]


# ----------------------------
# FSW Colorize
# ----------------------------

fsw_colors: List[str] = [
    "#0000CC",
    "#CC0000",
    "#FF0099",
    "#006600",
    "#000000",
    "#884411",
    "#FF9900",
]


def fsw_colorize(key: str) -> str:
    """
    Function that returns the standardized color for a symbol.

    Args:
        key: an FSW symbol key

    Returns:
        name of standardized color for symbol

    Example:
        >>> fsw_colorize('S10000')
        '#0000CC'
    """
    if not isinstance(key, str):
        return "#000000"
    parsed = fsw_parse_symbol(key)
    color = "#000000"
    if symbol := parsed.get("symbol"):
        dec = int(symbol[1:4], 16)
        index = next(
            (i for i, val in enumerate(fsw_structure_category) if val > dec), -1
        )
        color = fsw_colors[6 if index < 0 else index - 1]
    return color


# ----------------------------
# FSW Parsing
# ----------------------------


def fsw_parse_symbol(fsw_sym: str) -> SymbolObject:
    """
    Parse an FSW symbol with optional coordinate and style string.

    Args:
        fsw_sym: an FSW symbol string

    Returns:
        Dictionary with 'symbol', 'coord', 'style' keys

    Example:
        >>> fsw_parse_symbol('S10000500x500-C')
        {'symbol': 'S10000', 'coord': [500, 500], 'style': '-C'}
    """
    pattern = re.compile(
        rf"^({fsw_pattern_symbol})({fsw_pattern_coord})?({style_pattern_full})?"
    )
    m = pattern.match(fsw_sym)
    if not m:
        return {}
    return drop_none(
        {
            "symbol": m.group(1),
            "coord": fsw_to_coord(m.group(2)) if m.group(2) else None,
            "style": m.group(3),
        }
    )  # type: ignore[return-value]


def fsw_parse_sign(fsw_sign: str) -> SignObject:
    """
    Parse an FSW sign with optional style string.

    Args:
        fsw_sign: an FSW sign string

    Returns:
        Dictionary with 'sequence', 'box', 'max', 'spatials', 'style' keys

    Example:
        >>> fsw_parse_sign('AS10011S10019S2e704S2e748M525x535S2e748483x510S10011501x466S2e704510x500S10019476x475-C')
        {'sequence': ['S10011', 'S10019', 'S2e704', 'S2e748'],
         'box': 'M',
         'max': [525, 535],
         'spatials': [{'symbol': 'S2e748', 'coord': [483, 510]},
                      {'symbol': 'S10011', 'coord': [501, 466]},
                      {'symbol': 'S2e704', 'coord': [510, 500]},
                      {'symbol': 'S10019', 'coord': [476, 475]}],
         'style': '-C'}
    """
    pattern = re.compile(
        rf"^({fsw_pattern_prefix})?({fsw_pattern_signbox})({style_pattern_full})?"
    )
    m = pattern.match(fsw_sign)
    if not m:
        return {}
    prefix = m.group(1)
    signbox = m.group(2)
    sequence = re.findall(r".{6}", prefix[1:]) if prefix else None
    box = signbox[0]
    max_coord = fsw_to_coord(signbox[1:8])
    spatials_str = signbox[8:] if len(signbox) > 8 else ""
    spatials = (
        [
            {"symbol": s[:6], "coord": fsw_to_coord(s[6:])}
            for s in re.findall(r".{13}", spatials_str)
        ]
        if spatials_str
        else None
    )
    return drop_none(
        {
            "sequence": sequence,
            "box": box,
            "max": max_coord,
            "spatials": spatials,
            "style": m.group(3),
        }
    )  # type: ignore[return-value]


def fsw_parse_text(fsw_text: str) -> List[str]:
    """
    Parse an FSW text into signs and punctuations.

    Args:
        fsw_text: an FSW text string

    Returns:
        List of FSW signs and punctuations

    Example:
        >>> fsw_parse_text('AS14c20S27106M518x529S14c20481x471S27106503x489 AS18701S1870aS2e734S20500M518x533S1870a489x515S18701482x490S20500508x496S2e734500x468 S38800464x496')
        ['AS14c20S27106M518x529S14c20481x471S27106503x489',
         'AS18701S1870aS2e734S20500M518x533S1870a489x515S18701482x490S20500508x496S2e734500x468',
         'S38800464x496']
    """
    if not isinstance(fsw_text, str):
        return []
    pattern = re.compile(
        rf"(?:{fsw_pattern_prefix})?(?:{fsw_pattern_signbox})(?:{style_pattern_full})?|{fsw_pattern_spatial}(?:{style_pattern_full})?"
    )
    return pattern.findall(fsw_text)


# ----------------------------
# FSW Compose
# ----------------------------


def fsw_compose_symbol(fsw_sym_object: SymbolObject) -> Optional[str]:
    """
    Function to compose an fsw symbol with optional coordinate and style string.

    Args:
        fsw_sym_object: an fsw symbol object

    Returns:
        an fsw symbol string

    Example:
        >>> fsw_compose_symbol({'symbol': 'S10000', 'coord': [480, 480], 'style': '-C'})
        'S10000480x480-C'
    """
    symbol = fsw_sym_object.get("symbol")
    if not isinstance(symbol, str):
        return None
    symbol_match = re.match(f"^({fsw_pattern_symbol})$", symbol)
    if not symbol_match:
        return None
    symbol = symbol_match.group(1)

    coord = fsw_sym_object.get("coord")
    coord_str = ""
    if coord and isinstance(coord, list) and len(coord) == 2:
        x = str(coord[0])
        y = str(coord[1])
        coord_candidate = f"{x}x{y}"
        coord_match = re.match(f"^({fsw_pattern_coord})$", coord_candidate)
        if coord_match:
            coord_str = coord_match.group(1)

    style_str = fsw_sym_object.get("style")
    style_candidate = ""
    if isinstance(style_str, str):
        style_match = re.match(f"^({style_pattern_full})", style_str)
        if style_match:
            style_candidate = style_match.group(1)

    return symbol + coord_str + style_candidate


def fsw_compose_sign(fsw_sign_object: SignObject) -> Optional[str]:
    """
    Function to compose an fsw sign with style string.

    Args:
        fsw_sign_object: an fsw sign object

    Returns:
        an fsw sign string

    Example:
        >>> fsw_compose_sign({
        ...     'sequence': ['S10011', 'S10019', 'S2e704', 'S2e748'],
        ...     'box': 'M',
        ...     'max': [525, 535],
        ...     'spatials': [
        ...         {'symbol': 'S2e748', 'coord': [483, 510]},
        ...         {'symbol': 'S10011', 'coord': [501, 466]},
        ...         {'symbol': 'S2e704', 'coord': [510, 500]},
        ...         {'symbol': 'S10019', 'coord': [476, 475]}
        ...     ],
        ...     'style': '-C'
        ... })
        'AS10011S10019S2e704S2e748M525x535S2e748483x510S10011501x466S2e704510x500S10019476x475-C'
    """
    box = fsw_sign_object.get("box", "")
    box_match = re.match(f"^({fsw_pattern_box})$", box)
    if not box_match:
        return None
    box = box_match.group(1)

    max_coord = fsw_sign_object.get("max")
    max_str = ""
    if max_coord and isinstance(max_coord, list) and len(max_coord) == 2:
        x = str(max_coord[0])
        y = str(max_coord[1])
        max_candidate = f"{x}x{y}"
        max_match = re.match(f"^({fsw_pattern_coord})$", max_candidate)
        if max_match:
            max_str = max_match.group(1)
    if not max_str:
        return None

    prefix = ""
    sequence = fsw_sign_object.get("sequence")
    if sequence and isinstance(sequence, list):
        prefix_parts = []
        for key in sequence:
            key_match = re.match(f"^({fsw_pattern_null_or_symbol})$", key)
            if key_match:
                prefix_parts.append(key_match.group(1))
        prefix = "A" + "".join(prefix_parts) if prefix_parts else ""

    signbox = ""
    spatials = fsw_sign_object.get("spatials")
    if spatials and isinstance(spatials, list):
        signbox_parts = []
        for spatial in spatials:
            sym = spatial.get("symbol")
            if not isinstance(sym, str):
                continue
            sym_match = re.match(f"^({fsw_pattern_symbol})$", sym)
            if not sym_match:
                continue
            sym = sym_match.group(1)

            coord = spatial.get("coord")
            coord_str = ""
            if coord and isinstance(coord, list) and len(coord) == 2:
                x = str(coord[0])
                y = str(coord[1])
                coord_candidate = f"{x}x{y}"
                coord_match = re.match(f"^({fsw_pattern_coord})$", coord_candidate)
                if coord_match:
                    coord_str = coord_match.group(1)
            if not coord_str:
                continue

            signbox_parts.append(sym + coord_str)
        signbox = "".join(signbox_parts)

    style_str = fsw_sign_object.get("style")
    style_candidate = ""
    if isinstance(style_str, str):
        style_match = re.match(f"^({style_pattern_full})$", style_str)
        if style_match:
            style_candidate = style_match.group(1)

    return prefix + box + max_str + signbox + style_candidate


# ----------------------------
# FSW Info
# ----------------------------


def fsw_info(fsw: str) -> SegmentInfo:
    """
    Function to gather sizing information about an fsw sign or symbol.

    Args:
        fsw: an fsw sign or symbol

    Returns:
        information about the fsw string

    Example:
        >>> fsw_info('AS14c20S27106L518x529S14c20481x471S27106503x489-P10Z2')
        {
            'minX': 481,
            'minY': 471,
            'width': 37,
            'height': 58,
            'lane': -1,
            'padding': 10,
            'segment': 'sign',
            'zoom': 2
        }
    """
    lanes = {"B": 0, "L": -1, "M": 0, "R": 1}
    parsed_sign = fsw_parse_sign(fsw)
    width: Optional[int] = None
    height: Optional[int] = None
    segment: str = "none"
    x1: int = 490
    y1: int = 490
    lane: int = 0

    if spatials := parsed_sign.get("spatials"):
        x_coords = [spatial["coord"][0] for spatial in spatials]
        y_coords = [spatial["coord"][1] for spatial in spatials]
        x1 = min(x_coords)
        y1 = min(y_coords)
        x2, y2 = parsed_sign["max"]
        width = x2 - x1
        height = y2 - y1
        segment = "sign"
        lane = lanes[parsed_sign["box"]]
        style = style_parse(parsed_sign.get("style", ""))
    else:
        parsed_symbol = fsw_parse_symbol(fsw)
        lane = lanes["M"]
        if coord := parsed_symbol.get("coord"):
            x1, y1 = coord
            width = (500 - x1) * 2
            height = (500 - y1) * 2
            segment = "symbol"
        style = style_parse(parsed_symbol.get("style", ""))

    zoom = style.get("zoom", 1)
    padding = style.get("padding", 0)

    return {
        "minX": x1,
        "minY": y1,
        "width": width or 20,
        "height": height or 20,
        "segment": segment,
        "lane": lane,
        "padding": padding,
        "zoom": zoom,
    }


# ----------------------------
# FSW Columns
# ----------------------------

fsw_column_defaults: ColumnOptions = {
    "height": 500,
    "width": 150,
    "offset": 50,
    "pad": 20,
    "margin": 5,
    "dynamic": False,
    "punctuation": {
        "spacing": True,
        "pad": 30,
        "pull": True,
    },
    "style": {
        "detail": ["black", "white"],
        "zoom": 1,
    },
}


def fsw_column_defaults_merge(options: Optional[ColumnOptions] = None) -> ColumnOptions:
    """
    Function to merge an object of column options with default values.

    Args:
        options: object of column options

    Returns:
        object of column options merged with column defaults

    Example:
        >>> fsw_column_defaults_merge({'height': 500, 'width': 150})
        {'height': 500, 'width': 150, 'offset': 50, ...}
    """
    if not isinstance(options, dict):
        options = {}
    merged = {**fsw_column_defaults, **options}
    merged["punctuation"] = {
        **fsw_column_defaults["punctuation"],
        **(options.get("punctuation") or {}),
    }
    merged["style"] = {**fsw_column_defaults["style"], **(options.get("style") or {})}
    return drop_none(merged)  # type: ignore[return-value]


def fsw_columns(
    fsw_text: str, options: Optional[ColumnOptions] = None
) -> ColumnsResult:
    """
    Function to transform an FSW text to an array of columns.

    Args:
        fsw_text: FSW text of signs and punctuation
        options: object of column options

    Returns:
        object of column options, widths array, and column data

    Example:
        >>> fsw_columns('AS14c20S27106M518x529S14c20481x471S27106503x489 AS18701S1870aS2e734S20500M518x533S1870a489x515S18701482x490S20500508x496S2e734500x468 S38800464x496', {'height': 500, 'width': 150})
        {'options': {...}, 'widths': [150], 'columns': [[{'x': 56, 'y': 20, ...}, ...]]}
    """
    if not isinstance(fsw_text, str):
        return {}
    values = fsw_column_defaults_merge(options)
    if values["style"]["zoom"] == "x":
        values["style"]["zoom"] = 1.0

    input_text = fsw_parse_text(fsw_text)
    if not input_text:
        return {}

    cursor = 0.0
    cols: List[List[ColumnSegment]] = []
    col: List[ColumnSegment] = []
    plus = 0
    center = values["width"] // 2
    max_height = values["height"] - values["margin"]
    pullable = True
    finalize = False

    for val in input_text:
        informed = fsw_info(val)
        if informed["zoom"] == "x":
            informed["zoom"] = 1.0

        cursor += plus
        if values["punctuation"]["spacing"]:
            cursor += values["pad"] if informed["segment"] == "sign" else 0
        else:
            cursor += values["pad"]

        finalize = (cursor + informed["height"]) > max_height

        if (
            informed["segment"] == "symbol"
            and values["punctuation"]["pull"]
            and pullable
        ):
            finalize = False
            pullable = False

        if not col:
            finalize = False

        if finalize:
            cursor = values["pad"]
            cols.append(col)
            col = []
            pullable = True

        item: ColumnSegment = {
            **informed,
            "x": int(
                center
                + (values["offset"] * informed["lane"])
                - (
                    (500 - informed["minX"])
                    * to_zoom(informed["zoom"])
                    * to_zoom(values["style"]["zoom"])
                )
            ),
            "y": int(cursor),
            "text": val,
        }
        col.append(item)
        cursor += (
            informed["height"]
            * to_zoom(informed["zoom"])
            * to_zoom(values["style"]["zoom"])
        )

        if values["punctuation"]["spacing"]:
            plus = (
                values["pad"]
                if informed["segment"] == "sign"
                else values["punctuation"]["pad"]
            )
        else:
            plus = values["pad"]

    if col:
        cols.append(col)

    # Over-height adjustment for pulled punctuation
    if values["punctuation"]["pull"]:
        for c in cols:
            last = c[-1]
            diff = (last["y"] + last["height"]) - (values["height"] - values["margin"])
            if diff > 0:
                adj = (diff // len(c)) + 1
                for i, item in enumerate(c):
                    item["y"] -= adj * i + adj

    # Contract, expand, adjust widths
    widths: List[int] = []
    for c in cols:
        mins = [center - values["offset"] - values["pad"]]
        maxs = [center + values["offset"] + values["pad"]]
        for item in c:
            mins.append(item["x"] - values["pad"])
            maxs.append(item["x"] + item["width"] + values["pad"])
        min_val = min(mins)
        max_val = max(maxs)

        width = values["width"]
        adj = 0
        if not values["dynamic"]:
            adj = center - ((min_val + max_val) // 2)
        else:
            width = max_val - min_val
            adj = -min_val

        for item in c:
            item["x"] += adj
        widths.append(width)

    return {"options": values, "widths": widths, "columns": cols}


# ----------------------------
# FSW Tokenizer
# ----------------------------

DEFAULT_SPECIAL_TOKENS: List[SpecialToken] = [
    {"index": 0, "name": "UNK", "value": "[UNK]"},
    {"index": 1, "name": "PAD", "value": "[PAD]"},
    {"index": 2, "name": "CLS", "value": "[CLS]"},
    {"index": 3, "name": "SEP", "value": "[SEP]"},
]


def _generate_tokens() -> List[str]:
    sequence = ["A"]
    signbox = ["B", "L", "M", "R"]
    null_token = ["S000"]
    base_symbols = [f"S{i:03x}" for i in range(0x100, 0x38C)]
    rows = [f"r{i:x}" for i in range(16)]
    cols = [f"c{i:x}" for i in range(6)]
    positions = [f"p{i}" for i in range(250, 751)]
    return sequence + signbox + null_token + base_symbols + rows + cols + positions


@dataclass
class SpecialTokenMappings:
    by_index: Dict[int, SpecialToken]
    by_name: Dict[str, SpecialToken]
    by_value: Dict[str, SpecialToken]

    def get_by_index(self, index: int) -> SpecialToken:
        unk = next(t for t in self.by_index.values() if t["name"] == "UNK")
        return self.by_index.get(index, unk)

    def get_by_name(self, name: str) -> SpecialToken:
        return self.by_name.get(name, self.by_name["UNK"])

    def get_by_value(self, value: str) -> SpecialToken:
        return self.by_value.get(value, self.by_name["UNK"])

    def get_all_values(self) -> List[str]:
        return [t["value"] for t in self.by_index.values()]

    def get_all_indices(self) -> List[int]:
        return [t["index"] for t in self.by_index.values()]


def _create_special_token_mappings(
    special_tokens: List[SpecialToken],
) -> SpecialTokenMappings:
    by_index: Dict[int, SpecialToken] = {}
    by_name: Dict[str, SpecialToken] = {}
    by_value: Dict[str, SpecialToken] = {}
    indices: Set[int] = set()

    for token in special_tokens:
        if token["index"] in indices:
            raise ValueError(f"Duplicate token index: {token['index']}")
        indices.add(token["index"])
        by_index[token["index"]] = token
        by_name[token["name"]] = token
        by_value[token["value"]] = token

    return SpecialTokenMappings(by_index, by_name, by_value)


def _create_token_mappings(
    tokens: List[str],
    special_token_mappings: SpecialTokenMappings,
    starting_index: int,
) -> TokenizerMappings:
    i2s: Dict[int, str] = {}
    s2i: Dict[str, int] = {}

    # Add special tokens first
    for special_token in special_token_mappings.by_index.values():
        i2s[special_token["index"]] = special_token["value"]
        s2i[special_token["value"]] = special_token["index"]

    # Add regular tokens
    for i, reg_token in enumerate(tokens):
        index = starting_index + i
        i2s[index] = reg_token
        s2i[reg_token] = index

    return {"i2s": i2s, "s2i": s2i}


def fsw_tokenize(
    fsw: str,
    sequence: bool = True,
    signbox: bool = True,
    sep: Optional[str] = "[SEP]",
) -> List[str]:
    """
    Tokenizes an FSW string into an array of tokens

    Args:
        fsw: FSW string to tokenize
        sequence: Whether to include sequence tokens
        signbox: Whether to include signbox tokens
        sep: Separator token

    Returns:
        Array of tokens

    Example:
        >>> fsw_tokenize("AS10e00M507x515S10e00492x485", sequence=False, sep=None)
        ['M', 'p507', 'p515', 'S10e', 'c0', 'r0', 'p492', 'p485']
    """

    def tokenize_symbol(symbol: str) -> List[str]:
        return [symbol[:4], f"c{symbol[4]}", f"r{symbol[5]}"]

    def tokenize_coord(coord: List[int]) -> List[str]:
        return [f"p{c}" for c in coord]

    segments = fsw_parse_text(fsw)
    result: List[str] = []

    for fsw_segment in segments:
        tokens: List[str] = []

        if re.search(r"[BLMR]", fsw_segment):
            sign = fsw_parse_sign(fsw_segment)

            if sign.get("sequence") and sequence:
                tokens.extend(["A"])
                for seq_item in sign["sequence"]:
                    tokens.extend(tokenize_symbol(seq_item))

            if signbox:
                tokens.append(sign["box"])
                tokens.extend(tokenize_coord(sign["max"]))
                for spatial in sign.get("spatials", []):
                    tokens.extend(tokenize_symbol(spatial["symbol"]))
                    tokens.extend(tokenize_coord(spatial["coord"]))

        else:
            parsed = fsw_parse_symbol(fsw_segment)

            if not signbox and not sequence:
                continue

            if not signbox and sequence:
                tokens = ["A"] + tokenize_symbol(parsed["symbol"])
            else:
                coord = parsed.get("coord")
                if coord:
                    rev_coord = [1000 - c for c in coord]
                    tokens = (
                        ["M"]
                        + tokenize_coord(rev_coord)
                        + tokenize_symbol(parsed["symbol"])
                        + tokenize_coord(coord)
                    )

        if tokens and sep:
            tokens.append(sep)
        result.extend(tokens)

    return result


def fsw_detokenize(
    tokens: List[str],
    special_tokens: List[SpecialToken] = DEFAULT_SPECIAL_TOKENS,
) -> str:
    """
    Converts an array of tokens back into an FSW string

    Args:
        tokens: Array of tokens to convert
        special_tokens: Array of special token objects to filter out

    Returns:
        FSW string

    Example:
        >>> fsw_detokenize(['M', 'p507', 'p515', 'S10e', 'c0', 'r0', 'p492', 'p485'])
        "M507x515S10e00492x485"
    """
    special_values = {t["value"] for t in special_tokens}
    filtered = [t for t in tokens if t not in special_values]
    joined = " ".join(filtered)
    joined = re.sub(r"p(\d{3})\s+p(\d{3})", r"\1x\2", joined)
    joined = re.sub(r" c(\d)\d? r(.)", r"\1\2", joined)
    joined = re.sub(r" c(\d)\d?", r"\g<1>0", joined)
    joined = re.sub(r" r(.)", r"0\1", joined)
    joined = joined.replace(" ", "")
    joined = re.sub(r"(\d)([BLMR])", r"\1 \2", joined)
    joined = re.sub(r"(\d)(AS)", r"\1 \2", joined)
    joined = re.sub(
        r"(A(?:S00000|S[123][0-9a-f]{2}[0-5][0-9a-f])+)( )([BLMR])", r"\1\3", joined
    )
    return joined


def fsw_chunk_tokens(
    tokens: List[str],
    chunk_size: int,
    cls: str = "[CLS]",
    sep: str = "[SEP]",
    pad: str = "[PAD]",
) -> List[List[str]]:
    """
    Splits tokens into chunks of specified size while preserving sign boundaries

    Args:
        tokens: Array of tokens to chunk
        chunk_size: Maximum size of each chunk
        cls: CLS token
        sep: SEP token
        pad: PAD token

    Returns:
        Array of token chunks
    """
    if chunk_size < 60:
        raise ValueError(
            "Chunk size must be at least 60 tokens to accommodate a typical sign"
        )

    chunks: List[List[str]] = []
    token_index = 0

    while token_index < len(tokens):
        current_chunk = [cls]

        while token_index < len(tokens):
            look_ahead = token_index
            while look_ahead < len(tokens) and tokens[look_ahead] != sep:
                look_ahead += 1

            sign_size = look_ahead - token_index + 1

            if len(current_chunk) + sign_size > chunk_size - 1:
                break

            current_chunk.extend(tokens[token_index : look_ahead + 1])
            token_index = look_ahead + 1

        while len(current_chunk) < chunk_size:
            current_chunk.append(pad)

        chunks.append(current_chunk)

    return chunks


class FSWTokenizer:
    """
    Creates a tokenizer object with encoding and decoding capabilities.

    Args:
        special_tokens: Special tokens list
        starting_index: Starting index for regular tokens

    Example:
        >>> t = FSWTokenizer()
        >>> t.encode('M507x515S10e00492x485')
        [7, 941, 949, 24, 678, 662, 926, 919, 3]
    """

    def __init__(
        self,
        special_tokens: List[SpecialToken] = DEFAULT_SPECIAL_TOKENS,
        starting_index: Optional[int] = None,
    ):
        self.special_tokens = _create_special_token_mappings(special_tokens)
        max_special = (
            max(self.special_tokens.get_all_indices())
            if self.special_tokens.get_all_indices()
            else -1
        )
        calculated_starting_index = starting_index or (max_special + 1)
        tokens = _generate_tokens()
        mappings = _create_token_mappings(
            tokens, self.special_tokens, calculated_starting_index
        )
        self.i2s: Dict[int, str] = mappings["i2s"]
        self.s2i: Dict[str, int] = mappings["s2i"]
        self.length = len(self.i2s)

    def vocab(self) -> List[str]:
        return list(self.i2s.values())

    def encode_tokens(self, tokens: List[str]) -> List[int]:
        return [
            self.s2i.get(t, self.special_tokens.get_by_value(t)["index"])
            for t in tokens
        ]

    def decode_tokens(self, indices: List[int]) -> List[str]:
        unk_value = self.special_tokens.get_by_name("UNK")["value"]
        return [self.i2s.get(i, unk_value) for i in indices]

    def encode(
        self, text: str, sequence: bool = True, signbox: bool = True
    ) -> List[int]:
        sep_value = self.special_tokens.get_by_name("SEP")["value"]
        tokens = fsw_tokenize(text, sequence=sequence, signbox=signbox, sep=sep_value)
        return self.encode_tokens(tokens)

    def decode(self, tokens: Union[List[int], List[List[int]]]) -> str:
        if not tokens:
            return ""

        if isinstance(tokens[0], list):
            decoded_chunks = [
                self.decode_tokens(cast(List[int], chunk)) for chunk in tokens
            ]
            flat_tokens = [t for chunk in decoded_chunks for t in chunk]
            return fsw_detokenize(
                flat_tokens, list(self.special_tokens.by_index.values())
            )

        decoded_tokens = self.decode_tokens(cast(List[int], tokens))
        return fsw_detokenize(
            decoded_tokens, list(self.special_tokens.by_index.values())
        )

    def chunk(self, tokens: List[str], chunk_size: int) -> List[List[str]]:
        return fsw_chunk_tokens(
            tokens,
            chunk_size,
            cls=self.special_tokens.get_by_name("CLS")["value"],
            sep=self.special_tokens.get_by_name("SEP")["value"],
            pad=self.special_tokens.get_by_name("PAD")["value"],
        )


__all__ = [
    "fsw_structure_kind",
    "fsw_structure_category",
    "fsw_structure_group",
    "fsw_structure_ranges",
    "fsw_is_type",
    "fsw_colors",
    "fsw_colorize",
    "fsw_parse_symbol",
    "fsw_parse_sign",
    "fsw_parse_text",
    "fsw_compose_symbol",
    "fsw_compose_sign",
    "fsw_info",
    "fsw_column_defaults",
    "fsw_column_defaults_merge",
    "fsw_columns",
    "fsw_tokenize",
    "fsw_detokenize",
    "fsw_chunk_tokens",
    "FSWTokenizer",
]
