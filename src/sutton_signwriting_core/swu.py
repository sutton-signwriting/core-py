"""
The swu module contains functions for handling SignWriting in Unicode (SWU) characters.

SWU characters definition: https://datatracker.ietf.org/doc/id/draft-slevinski-formal-signwriting-10.html#name-signwriting-in-unicode-swu

"""

import re
from typing import Dict, List, Optional, Tuple

from .datatypes import (
    SymbolObject,
    SignObject,
    SegmentInfo,
    ColumnOptions,
    ColumnSegment,
    ColumnsResult,
)

from .convert import drop_none, to_zoom, swu_to_coord, coord_to_swu, swu_to_code

from .regex import (
    style_pattern_full,
    swu_pattern_box,
    swu_pattern_null_or_symbol,
    swu_pattern_coord,
    swu_pattern_prefix,
    swu_pattern_signbox,
    swu_pattern_spatial,
    swu_pattern_symbol,
)

from .style import (
    style_parse,
)

# ----------------------------
# SWU structure constants (plane 4 code points)
# ----------------------------
swu_structure_kind: List[int] = [0x40001, 0x4EFA1, 0x4F2A1]

swu_structure_category: List[int] = [
    0x40001,
    0x461E1,
    0x4BCA1,
    0x4BFA1,
    0x4E8E1,
    0x4EFA1,
    0x4F2A1,
]

swu_structure_group: List[int] = [
    0x40001,
    0x40541,
    0x40B41,
    0x41981,
    0x41C81,
    0x43241,
    0x43D81,
    0x445C1,
    0x44CE1,
    0x45BE1,
    0x461E1,
    0x46841,
    0x46FC1,
    0x47FE1,
    0x485E1,
    0x49301,
    0x49E41,
    0x4A4A1,
    0x4AFE1,
    0x4B521,
    0x4BCA1,
    0x4BFA1,
    0x4C3C1,
    0x4CFC1,
    0x4D621,
    0x4E161,
    0x4E8E1,
    0x4EC41,
    0x4EFA1,
    0x4F2A1,
]

swu_structure_ranges: Dict[str, Tuple[int, int]] = {
    "all": (0x40001, 0x4F480),
    "writing": (0x40001, 0x4EFA0),
    "hand": (0x40001, 0x461E0),
    "movement": (0x461E1, 0x4BCA0),
    "dynamic": (0x4BCA1, 0x4BFA0),
    "head": (0x4BFA1, 0x4E8E0),
    "hcenter": (0x4BFA1, 0x4E8E0),
    "vcenter": (0x4BFA1, 0x4EC40),
    "trunk": (0x4E8E1, 0x4EC40),
    "limb": (0x4EC41, 0x4EFA0),
    "location": (0x4EFA1, 0x4F2A0),
    "punctuation": (0x4F2A1, 0x4F480),
}


def swu_is_type(swu_char: str, type_name: str) -> bool:
    """
    Test whether an SWU character is of the given type/range.

    Args:
        swu_char: an SWU symbol
        type_name: the name of a symbol range

    Returns:
        True if symbol of specified type

    Example:
        >>> swu_is_type('񀀁', 'hand')
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
    if not (isinstance(swu_char, str) and len(swu_char) >= 1):
        return False
    code = ord(swu_char[0])
    rng = swu_structure_ranges.get(type_name)
    if not rng:
        return False
    return rng[0] <= code <= rng[1]


# ----------------------------
# SWU Colorize
# ----------------------------

swu_colors: List[str] = [
    "#0000CC",
    "#CC0000",
    "#FF0099",
    "#006600",
    "#000000",
    "#884411",
    "#FF9900",
]


def swu_colorize(sym: str) -> str:
    """
    Function that returns the standardized color for a symbol.

    Args:
        sym: an SWU symbol

    Returns:
        name of standardized color for symbol

    Example:
        >>> swu_colorize('񀀁')
        '#0000CC'
    """
    if not isinstance(sym, str):
        return "#000000"
    parsed = swu_parse_symbol(sym)
    color = "#000000"
    if symbol := parsed.get("symbol"):
        code = swu_to_code(symbol)
        index = next(
            (i for i, val in enumerate(swu_structure_category) if val > code), -1
        )
        color = swu_colors[6 if index < 0 else index - 1]
    return color


# ----------------------------
# SWU Parsing
# ----------------------------


def swu_parse_symbol(swu_sym: str) -> SymbolObject:
    """
    Parse an SWU symbol with optional coordinate and style string.

    Args:
        swu_sym: an SWU symbol string

    Returns:
        Dictionary with 'symbol', 'coord', 'style' keys


    Example:
        >>> swu_parse_symbol('񀀁𝤆𝤆-C')
        {'symbol': '񀀁', 'coord': [500, 500], 'style': '-C'}
    """
    pattern = re.compile(
        rf"^({swu_pattern_symbol})({swu_pattern_coord})?({style_pattern_full})?"
    )
    m = pattern.match(swu_sym)
    if not m:
        return {}
    return drop_none(
        {
            "symbol": m.group(1),
            "coord": swu_to_coord(m.group(2)) if m.group(2) else None,
            "style": m.group(3) if m.group(3) else None,
        }
    )  # type: ignore[return-value]


def swu_parse_sign(swu_sign: str) -> SignObject:
    """
    Parse an SWU sign with optional style string.

    Args:
        swu_sign: an SWU sign string

    Returns:
        Dictionary with 'sequence', 'box', 'max', 'spatials', 'style' keys

    Example:
        >>> swu_parse_sign('𝠀񀀒񀀚񋚥񋛩𝠃𝤟𝤩񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭-C')
        {'sequence': ['񀀒', '񀀚', '񋚥', '񋛩'],
         'box': '𝠃',
         'max': [525, 535],
         'spatials': [{'symbol': '񋛩', 'coord': [483, 510]},
                      {'symbol': '񀀒', 'coord': [501, 466]},
                      {'symbol': '񋚥', 'coord': [510, 500]},
                      {'symbol': '񀀚', 'coord': [476, 475]}],
         'style': '-C'}
    """
    pattern = re.compile(
        rf"^({swu_pattern_prefix})?({swu_pattern_signbox})({style_pattern_full})?"
    )
    m = pattern.match(swu_sign)
    if not m:
        return {}
    prefix = m.group(1)
    signbox = m.group(2)
    sequence = list(prefix[1:]) if prefix else None
    box = signbox[0]
    max_coord = swu_to_coord(signbox[1:3])
    spatials_str = signbox[3:] if len(signbox) > 3 else ""
    spatials_matches = re.findall(
        rf"({swu_pattern_symbol})({swu_pattern_coord})", spatials_str
    )
    spatials = (
        [
            {"symbol": sym, "coord": swu_to_coord(coord_str)}
            for sym, coord_str in spatials_matches
        ]
        if spatials_matches
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


def swu_parse_text(swu_text: str) -> List[str]:
    """
    Parse an SWU text into signs and punctuations.

    Args:
        swu_text: an SWU text string

    Returns:
        List of SWU signs and punctuations

    Example:
        >>> swu_parse_text('𝠀񁲡񈩧𝠃𝤘𝤣񁲡𝣳𝣩񈩧𝤉𝣻 𝠀񃊢񃊫񋛕񆇡𝠃𝤘𝤧񃊫𝣻𝤕񃊢𝣴𝣼񆇡𝤎𝤂񋛕𝤆𝣦 񏌁𝣢𝤂')
        ['𝠀񁲡񈩧𝠃𝤘𝤣񁲡𝣳𝣩񈩧𝤉𝣻',
         '𝠀񃊢񃊫񋛕񆇡𝠃𝤘𝤧񃊫𝣻𝤕񃊢𝣴𝣼񆇡𝤎𝤂񋛕𝤆𝣦',
         '񏌁𝣢𝤂']
    """
    if not isinstance(swu_text, str):
        return []
    pattern = re.compile(
        rf"(?:{swu_pattern_prefix})?(?:{swu_pattern_signbox})(?:{style_pattern_full})?|{swu_pattern_spatial}(?:{style_pattern_full})?"
    )
    return pattern.findall(swu_text)


# ----------------------------
# SWU Compose
# ----------------------------


def swu_compose_symbol(swu_sym_object: SymbolObject) -> Optional[str]:
    """
    Function to compose an swu symbol with optional coordinate and style string.

    Args:
        swu_sym_object: an swu symbol object

    Returns:
        an swu symbol string

    Example:
        >>> swu_compose_symbol({'symbol': '񀀁', 'coord': [500, 500], 'style': '-C'})
        '񀀁𝤆𝤆-C'
    """
    if not isinstance(swu_sym_object, dict):
        return None
    symbol = swu_sym_object.get("symbol")
    if not isinstance(symbol, str):
        return None
    symbol_match = re.match(f"^({swu_pattern_symbol})$", symbol)
    if not symbol_match:
        return None
    symbol = symbol_match.group(1)

    coord = swu_sym_object.get("coord")
    coord_str = ""
    if coord and isinstance(coord, list) and len(coord) == 2:
        coord_str = coord_to_swu(coord)

    style_str = swu_sym_object.get("style")
    style_candidate = ""
    if isinstance(style_str, str):
        style_match = re.match(f"^({style_pattern_full})", style_str)
        if style_match:
            style_candidate = style_match.group(1)

    return symbol + coord_str + style_candidate


def swu_compose_sign(swu_sign_object: SignObject) -> Optional[str]:
    """
    Function to compose an swu sign with style string.

    Args:
        swu_sign_object: an swu sign object

    Returns:
        an swu sign string

    Example:
        >>> swu_compose_sign({
        ...     'sequence': ['񀀒','񀀚','񋚥','񋛩'],
        ...     'box': '𝠃',
        ...     'max': [525, 535],
        ...     'spatials': [
        ...         {'symbol': '񋛩', 'coord': [483, 510]},
        ...         {'symbol': '񀀒', 'coord': [501, 466]},
        ...         {'symbol': '񋚥', 'coord': [510, 500]},
        ...         {'symbol': '񀀚', 'coord': [476, 475]}
        ...     ],
        ...     'style': '-C'
        ... })
        '𝠀񀀒񀀚񋚥񋛩𝠃𝤟𝤩񋛩𝣵𝤐񀀒𝤇𝣤񋚥𝤐𝤆񀀚𝣮𝣭-C'
    """
    box = swu_sign_object.get("box", "")
    box_match = re.match(f"^({swu_pattern_box})$", box)
    if not box_match:
        return None
    box = box_match.group(1)

    max_coord = swu_sign_object.get("max")
    max_str = ""
    if max_coord and isinstance(max_coord, list) and len(max_coord) == 2:
        max_str = coord_to_swu(max_coord)
    if not max_str:
        return None

    prefix = ""
    sequence = swu_sign_object.get("sequence")
    if sequence and isinstance(sequence, list):
        prefix_parts = []
        for key in sequence:
            key_match = re.match(f"^({swu_pattern_null_or_symbol})$", key)
            if key_match:
                prefix_parts.append(key_match.group(1))
        prefix = "\U0001D800" + "".join(prefix_parts) if prefix_parts else ""

    signbox = ""
    spatials = swu_sign_object.get("spatials")
    if spatials and isinstance(spatials, list):
        signbox_parts = []
        for spatial in spatials:
            sym = spatial.get("symbol")
            if not isinstance(sym, str):
                continue
            sym_match = re.match(f"^({swu_pattern_symbol})$", sym)
            if not sym_match:
                continue
            sym = sym_match.group(1)

            coord = spatial.get("coord")
            coord_str = ""
            if coord and isinstance(coord, list) and len(coord) == 2:
                coord_str = coord_to_swu(coord)
            if not coord_str:
                continue

            signbox_parts.append(sym + coord_str)
        signbox = "".join(signbox_parts)

    style_str = swu_sign_object.get("style")
    style_candidate = ""
    if isinstance(style_str, str):
        style_match = re.match(f"^({style_pattern_full})$", style_str)
        if style_match:
            style_candidate = style_match.group(1)

    return prefix + box + max_str + signbox + style_candidate


# ----------------------------
# SWU Info
# ----------------------------


def swu_info(swu: str) -> SegmentInfo:
    """
    Function to gather sizing information about an swu sign or symbol.

    Args:
        swu: an swu sign or symbol

    Returns:
        information about the swu string

    Example:
        >>> swu_info('𝠀񁲡񈩧𝠂𝤘𝤣񁲡𝣳𝣩񈩧𝤉𝣻-P10Z2')
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
    lanes = {"𝠁": 0, "𝠂": -1, "𝠃": 0, "𝠄": 1}
    parsed_sign = swu_parse_sign(swu)
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
        parsed_symbol = swu_parse_symbol(swu)
        lane = lanes["𝠃"]
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
# SWU Columns
# ----------------------------

swu_column_defaults: ColumnOptions = {
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


def swu_column_defaults_merge(options: Optional[ColumnOptions] = None) -> ColumnOptions:
    """
    Function to merge an object of column options with default values.

    Args:
        options: object of column options

    Returns:
        object of column options merged with column defaults

    Example:
        >>> swu_column_defaults_merge({'height': 500, 'width': 150})
        {'height': 500, 'width': 150, 'offset': 50, ...}
    """
    if not isinstance(options, dict):
        options = {}
    merged = {**swu_column_defaults, **options}
    merged["punctuation"] = {
        **swu_column_defaults["punctuation"],
        **(options.get("punctuation") or {}),
    }
    merged["style"] = {**swu_column_defaults["style"], **(options.get("style") or {})}
    return drop_none(merged)  # type: ignore[return-value]


def swu_columns(
    swu_text: str, options: Optional[ColumnOptions] = None
) -> ColumnsResult:
    """
    Function to transform an FSW text to an array of columns.

    Args:
        swu_text: FSW text of signs and punctuation
        options: object of column options

    Returns:
        object of column options, widths array, and column data

    Example:
        >>> swu_columns('𝠀񁲡񈩧𝠃𝤘𝤣񁲡𝣳𝣩񈩧𝤉𝣻 𝠀񃊢񃊫񋛕񆇡𝠃𝤘𝤧񃊫𝣻𝤕񃊢𝣴𝣼񆇡𝤎𝤂񋛕𝤆𝣦 񏌁𝣢𝤂', {'height': 500, 'width': 150})
        {'options': {...}, 'widths': [150], 'columns': [[{'x': 56, 'y': 20, ...}, ...]]}
    """
    if not isinstance(swu_text, str):
        return {}
    values = swu_column_defaults_merge(options)
    if values["style"]["zoom"] == "x":
        values["style"]["zoom"] = 1.0

    input_text = swu_parse_text(swu_text)
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
        informed = swu_info(val)
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


__all__ = [
    "swu_structure_kind",
    "swu_structure_category",
    "swu_structure_group",
    "swu_structure_ranges",
    "swu_is_type",
    "swu_colors",
    "swu_colorize",
    "swu_parse_symbol",
    "swu_parse_sign",
    "swu_parse_text",
    "swu_compose_symbol",
    "swu_compose_sign",
    "swu_info",
    "swu_column_defaults",
    "swu_column_defaults_merge",
    "swu_columns",
]
