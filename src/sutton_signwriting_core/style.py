"""
The style module contains regular expressions and functions for parsing and composing style strings.

Style string definition: https://datatracker.ietf.org/doc/id/draft-slevinski-formal-signwriting-10.html#name-styling-string
"""

import re
from typing import List, Optional, Union

from .datatypes import (
    DetailSym,
    StyleObject,
)

from .regex import (
    style_pattern_colorbase,
    style_pattern_detailsym,
    style_pattern_full_groups,
    style_pattern_full,
)

from .convert import to_zoom

# ----------------------------
# Style Parsing
# ----------------------------


def _prefix_color(color: str) -> str:
    if re.match(rf"^{style_pattern_colorbase}$", color):
        return (
            "#" + color
            if len(color) in (3, 6)
            and all(c in "0123456789abcdefABCDEF" for c in color)
            else color
        )
    return color


def style_parse(style_string: str) -> StyleObject:
    """
    Parse a style string to a structured dictionary.

    Args:
        style_string: a style string

    Returns:
        Dictionary with style elements

    Example:
        >>> style_parse('-CP10G_blue_D_red,Cyan_')
        {'colorize': True, 'padding': 10, 'background': 'blue', 'detail': ['red', 'Cyan']}
    """
    pattern = re.compile(rf"^{style_pattern_full_groups}")
    m = pattern.match(style_string) if isinstance(style_string, str) else None
    if not m:
        return {}

    res: StyleObject = {}

    colorize = True if m.group(1) else None
    if colorize is not None:
        res["colorize"] = colorize

    padding = int(m.group(2)[1:]) if m.group(2) else None
    if padding is not None:
        res["padding"] = padding

    background = None if not m.group(3) else _prefix_color(m.group(3)[2:-1])
    if background is not None:
        res["background"] = background

    detail = (
        None
        if not (s := m.group(4))
        else [_prefix_color(p.strip()) for p in s[2:-1].split(",")]
    )
    if detail is not None:
        res["detail"] = detail

    zoom_str = m.group(5)
    zoom: Optional[Union[int, float, str]] = None
    if zoom_str:
        zoom = "x" if zoom_str == "Zx" else float(zoom_str[1:])
    if zoom is not None:
        res["zoom"] = zoom

    detailsym: List[DetailSym] = []
    if detailsym_str := m.group(6):
        detailsym_matches = re.findall(style_pattern_detailsym, detailsym_str)
        for ds in detailsym_matches:
            index = int(ds[1:3])
            inner = ds[4:-1]
            det = [_prefix_color(p.strip()) for p in inner.split(",") if p]
            detailsym.append({"index": index, "detail": det})
    if detailsym:
        res["detailsym"] = detailsym

    classes = m.group(7) if m.group(7) else None
    if classes is not None:
        res["classes"] = classes

    id_ = m.group(8) if m.group(8) else None
    if id_ is not None:
        res["id"] = id_

    return res


# ----------------------------
# Style Compose
# ----------------------------


def style_compose(style_dict: StyleObject) -> Optional[str]:
    """
    Function to compose style string from dictionary.

    Args:
        style_dict: a dictionary of style elements with keys:
            - 'colorize': Optional[bool]
            - 'padding': Optional[int]
            - 'background': Optional[str]
            - 'detail': Optional[List[str]]
            - 'zoom': Optional[Union[float, str]]
            - 'detailsym': Optional[List[Dict]] (each with 'index': int, 'detail': List[str])
            - 'classes': Optional[str]
            - 'id': Optional[str]

    Returns:
        style string

    Example:
        >>> style_compose({
        ...     'colorize': True,
        ...     'padding': 10,
        ...     'background': 'blue',
        ...     'detail': ['red', 'Cyan'],
        ...     'zoom': 1.1,
        ...     'detailsym': [
        ...         {'index': 1, 'detail': ['#ff0', 'green']}
        ...     ]
        ... })
        '-CP10GblueDred,CyanZ1.1-D01#ff0,green_'
    """
    style1 = ""
    if style_dict.get("colorize"):
        style1 += "C"
    padding = style_dict.get("padding")
    if padding is not None:
        style1 += f"P{int(padding):02d}"
    background = style_dict.get("background")
    if background:
        style1 += f"G_{background.lstrip('#')}_"
    detail = style_dict.get("detail")
    if detail and isinstance(detail, list):
        style1 += f"D_{','.join(detail).lstrip('#')}_"
    zoom = style_dict.get("zoom")
    if zoom is not None:
        style1 += f"Z{zoom}"

    style2 = ""
    detailsym = style_dict.get("detailsym")
    if detailsym and isinstance(detailsym, list):
        detailsym_parts = []
        for ds in detailsym:
            index = ds.get("index")
            ds_detail = ds.get("detail")
            if index is not None and ds_detail and isinstance(ds_detail, list):
                detailsym_parts.append(
                    f"D{int(index):02d}_{','.join(ds_detail).lstrip('#')}_"
                )
        style2 += "".join(detailsym_parts)

    style3 = ""
    classes = style_dict.get("classes")
    if isinstance(classes, str):
        classes_match = re.match(f"^({style_dict.get('classes')})$", classes)
        if classes_match:
            style3 += classes_match.group(1)
    id_ = style_dict.get("id")
    if classes or id_:
        style3 += "!"
    if id_ and isinstance(id_, str):
        id_match = re.match(f"^({style_dict.get('id')})$", id_)
        if id_match:
            style3 += id_match.group(1) + "!"

    result = (
        "-"
        + style1
        + ("-" + style2 if style2 or style3 else "")
        + ("-" + style3 if style3 else "")
    )
    match = re.match(f"^({style_pattern_full})$", result)
    return match.group(1) if match else None


# ----------------------------
# Style RGB
# ----------------------------


def _rgb_to_arr(rgb: str) -> List[float]:
    if not isinstance(rgb, str):
        return [0.0, 0.0, 0.0]
    m = re.match(r"rgba?\((.+?)\)", rgb.lower())
    if not m:
        return [0.0, 0.0, 0.0]
    values = m.group(1).split(",")
    return [float(v.strip()) for v in values]


def _arr_to_hex(arr: List[float]) -> str:
    return "".join(f"{int(v):02x}" for v in arr[:3])


def style_rgb_to_hex(rgb: str, tolerance: float = 0.0) -> str:
    """
    Function to convert rgb color to hex or "transparent" if below tolerance.

    Args:
        rgb: an rgb color
        tolerance: max alpha for full transparency (default: 0)

    Returns:
        a hex color or "transparent"

    Examples:
        >>> style_rgb_to_hex("rgb(255,255,255)")
        'ffffff'
        >>> style_rgb_to_hex("rgba(255,255,255,0.5)",0.5)
        'transparent'
    """
    arr = _rgb_to_arr(rgb)
    if len(arr) == 4 and arr[3] <= tolerance:
        return "transparent"
    else:
        return _arr_to_hex(arr)


def style_rgba_to_hex(color: str, background: str) -> str:
    """
    Function to merge color with background based on alpha transparency

    Args:
        color: an rgba color
        background: an rgba background color

    Returns:
        a hex color or "transparent"

    Example:
        >>> style_rgba_to_hex("rgba(255,255,255,0.5)","rgb(0,0,0)")
        '7f7f7f'
    """
    b_arr = _rgb_to_arr(background)
    c_arr = _rgb_to_arr(color)
    alpha = c_arr[3] if len(c_arr) == 4 else 1.0
    if alpha == 0:
        return "transparent"
    else:
        merged = [(1 - alpha) * b_arr[i] + alpha * c_arr[i] for i in range(3)]
        return _arr_to_hex(merged)


# ----------------------------
# Style Merge
# ----------------------------


def style_merge(
    style1: Optional[StyleObject], style2: Optional[StyleObject]
) -> StyleObject:
    """
    Function to merge style dictionaries.

    Args:
        style1: a style dictionary
        style2: a style dictionary

    Returns:
        a style dictionary

    Example:
        >>> style_merge({'colorize': True}, {'zoom': 2})
        {'colorize': True, 'zoom': 2}
    """
    if not isinstance(style1, dict):
        style1 = {}
    if not isinstance(style2, dict):
        style2 = {}
    zoom1 = to_zoom(style1.get("zoom"))
    zoom2 = to_zoom(style2.get("zoom"))
    merged: StyleObject = {**style1, **style2}
    merged["zoom"] = zoom1 * zoom2
    return merged


__all__ = [
    "style_parse",
    "style_compose",
    "style_rgb_to_hex",
    "style_rgba_to_hex",
    "style_merge",
]
