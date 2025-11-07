import re

# ----------------------------
# Utility
# ----------------------------


def _non_capturing(pattern: str) -> str:
    """Convert a regex with capturing groups into a non-capturing equivalent."""
    return re.sub(r"\((?!\?)", "(?:", pattern)


# ----------------------------
# FSW patterns
# ----------------------------

fsw_pattern_null = r"S00000"
""""""
fsw_pattern_symbol = r"S[123][0-9a-f]{2}[0-5][0-9a-f]"
""""""
fsw_pattern_number = r"[0-9]{3}"
""""""
fsw_pattern_sort = r"A"
""""""
fsw_pattern_box = r"[BLMR]"
""""""

fsw_pattern_null_or_symbol = rf"(?:{fsw_pattern_null}|{fsw_pattern_symbol})"
""""""
fsw_pattern_prefix = rf"(?:{fsw_pattern_sort}{fsw_pattern_null_or_symbol}+)"
""""""
fsw_pattern_coord = rf"{fsw_pattern_number}x{fsw_pattern_number}"
""""""
fsw_pattern_spatial = rf"{fsw_pattern_symbol}{fsw_pattern_coord}"
""""""
fsw_pattern_signbox = rf"{fsw_pattern_box}{fsw_pattern_coord}(?:{fsw_pattern_spatial})*"
""""""
fsw_pattern_sign = rf"{fsw_pattern_prefix}?{fsw_pattern_signbox}"
""""""
fsw_pattern_sortable = rf"{fsw_pattern_prefix}{fsw_pattern_signbox}"
""""""


# ----------------------------
# FSW Query patterns
# ----------------------------

fswquery_pattern_null = fsw_pattern_null
""""""
fswquery_pattern_base = r"[123][0-9a-f]{2}"
""""""
fswquery_pattern_coord = rf"(?:{fsw_pattern_coord})?"
""""""
fswquery_pattern_var = r"V[0-9]+"
""""""

fswquery_pattern_symbol = rf"S{fswquery_pattern_base}[0-5u][0-9a-fu]"
""""""
fswquery_pattern_null_or_symbol = (
    rf"(?:{fswquery_pattern_null}|{fswquery_pattern_symbol})"
)
""""""
fswquery_pattern_range = rf"R{fswquery_pattern_base}t{fswquery_pattern_base}"
""""""
fswquery_pattern_item = (
    rf"(?:{fswquery_pattern_null}|{fswquery_pattern_symbol}|{fswquery_pattern_range})"
)
""""""
fswquery_pattern_list = rf"{fswquery_pattern_item}(?:o{fswquery_pattern_item})*"
""""""
fswquery_pattern_prefix = rf"(?:A(?:{fswquery_pattern_list})+)?T"
""""""
fswquery_pattern_signbox = rf"(?:{fswquery_pattern_list}{fswquery_pattern_coord})*"
""""""
fswquery_pattern_full = rf"Q({fswquery_pattern_prefix})?({fswquery_pattern_signbox})?({fswquery_pattern_var})?(-?)"
""""""

# ----------------------------
# Style patterns
# ----------------------------
style_pattern_colorize = r"C"
""""""
style_pattern_colorhex = r"(?:[0-9a-fA-F]{3}){1,2}"
""""""
style_pattern_colorname = r"[a-zA-Z]+"
""""""
style_pattern_padding = r"P[0-9]{2}"
""""""
style_pattern_zoom = r"Z(?:[0-9]+(?:\.[0-9]+)?|x)"
""""""
style_pattern_classbase = r"-?[_a-zA-Z][_a-zA-Z0-9-]{0,100}"
""""""
style_pattern_id = r"[a-zA-Z][_a-zA-Z0-9-]{0,100}"
""""""

style_pattern_colorbase = rf"(?:{style_pattern_colorhex}|{style_pattern_colorname})"
""""""
style_pattern_color = rf"_{style_pattern_colorbase}_"
""""""
style_pattern_colors = rf"_{style_pattern_colorbase}(?:,{style_pattern_colorbase})?_"
""""""
style_pattern_background = rf"G{style_pattern_color}"
""""""
style_pattern_detail = rf"D{style_pattern_colors}"
""""""
style_pattern_detailsym = rf"D[0-9]{{2}}{style_pattern_colors}"
""""""
style_pattern_classes = rf"{style_pattern_classbase}(?: {style_pattern_classbase})*"
""""""
style_pattern_full_groups = (
    rf"-({style_pattern_colorize})?({style_pattern_padding})?({style_pattern_background})?"
    rf"({style_pattern_detail})?({style_pattern_zoom})?(?:-((?:{style_pattern_detailsym})*))?"
    rf"(?:-({style_pattern_classes})?!(?:({style_pattern_id})!)?)?"
)
""""""
style_pattern_full = _non_capturing(style_pattern_full_groups)
""""""

# ----------------------------
# SWU patterns
# ----------------------------

swu_pattern_null = "\\U00040000"
""""""
swu_pattern_symbol = "[\\U00040001-\\U0004F480]"
""""""
swu_pattern_number = "[\\U0001D80C-\\U0001D9FF]"
""""""
swu_pattern_sort = "\\U0001D800"
""""""
swu_pattern_box = "[\\U0001D801-\\U0001D804]"
""""""

swu_pattern_null_or_symbol = rf"(?:{swu_pattern_null}|{swu_pattern_symbol})"
""""""
swu_pattern_prefix = rf"(?:{swu_pattern_sort}{swu_pattern_null_or_symbol}+)"
""""""
swu_pattern_coord = rf"{swu_pattern_number}{{2}}"
""""""
swu_pattern_spatial = rf"{swu_pattern_symbol}{swu_pattern_coord}"
""""""
swu_pattern_signbox = rf"{swu_pattern_box}{swu_pattern_coord}(?:{swu_pattern_spatial})*"
""""""
swu_pattern_sign = rf"{swu_pattern_prefix}?{swu_pattern_signbox}"
""""""
swu_pattern_sortable = rf"{swu_pattern_prefix}{swu_pattern_signbox}"
""""""


# ----------------------------
# SWU Query patterns
# ----------------------------
swuquery_pattern_null = swu_pattern_null
""""""
swuquery_pattern_base = swu_pattern_symbol
""""""
swuquery_pattern_coord = rf"(?:{swu_pattern_number}{{2}})?"
""""""
swuquery_pattern_var = r"V[0-9]+"
""""""

swuquery_pattern_symbol = rf"{swuquery_pattern_base}f?r?"
""""""
swuquery_pattern_null_or_symbol = (
    rf"(?:{swuquery_pattern_null}|{swuquery_pattern_symbol})"
)
""""""
swuquery_pattern_range = rf"R{swuquery_pattern_base}{swuquery_pattern_base}"
""""""
swuquery_pattern_item = (
    rf"(?:{swuquery_pattern_null}|{swuquery_pattern_symbol}|{swuquery_pattern_range})"
)
""""""
swuquery_pattern_list = rf"{swuquery_pattern_item}(?:o{swuquery_pattern_item})*"
""""""
swuquery_pattern_prefix = rf"(?:A(?:{swuquery_pattern_list})+)?T"
""""""
swuquery_pattern_signbox = rf"(?:{swuquery_pattern_list}{swuquery_pattern_coord})*"
""""""
swuquery_pattern_full = rf"Q({swuquery_pattern_prefix})?({swuquery_pattern_signbox})?({swuquery_pattern_var})?(-?)"
""""""

# ----------------------------
# Exports
# ----------------------------
__all__ = [
    # FSW patterns
    "fsw_pattern_null",
    "fsw_pattern_symbol",
    "fsw_pattern_number",
    "fsw_pattern_sort",
    "fsw_pattern_box",
    "fsw_pattern_null_or_symbol",
    "fsw_pattern_prefix",
    "fsw_pattern_coord",
    "fsw_pattern_spatial",
    "fsw_pattern_signbox",
    "fsw_pattern_sign",
    "fsw_pattern_sortable",
    # FSW Query patterns
    "fswquery_pattern_null",
    "fswquery_pattern_base",
    "fswquery_pattern_coord",
    "fswquery_pattern_var",
    "fswquery_pattern_symbol",
    "fswquery_pattern_null_or_symbol",
    "fswquery_pattern_range",
    "fswquery_pattern_item",
    "fswquery_pattern_list",
    "fswquery_pattern_prefix",
    "fswquery_pattern_signbox",
    "fswquery_pattern_full",
    # Style patterns
    "style_pattern_colorize",
    "style_pattern_colorhex",
    "style_pattern_colorname",
    "style_pattern_padding",
    "style_pattern_zoom",
    "style_pattern_classbase",
    "style_pattern_id",
    "style_pattern_colorbase",
    "style_pattern_color",
    "style_pattern_colors",
    "style_pattern_background",
    "style_pattern_detail",
    "style_pattern_detailsym",
    "style_pattern_classes",
    "style_pattern_full_groups",
    "style_pattern_full",
    # SWU patterns
    "swu_pattern_null",
    "swu_pattern_symbol",
    "swu_pattern_number",
    "swu_pattern_sort",
    "swu_pattern_box",
    "swu_pattern_null_or_symbol",
    "swu_pattern_prefix",
    "swu_pattern_coord",
    "swu_pattern_spatial",
    "swu_pattern_signbox",
    "swu_pattern_sign",
    "swu_pattern_sortable",
    # SWU Query patterns
    "swuquery_pattern_null",
    "swuquery_pattern_base",
    "swuquery_pattern_coord",
    "swuquery_pattern_var",
    "swuquery_pattern_symbol",
    "swuquery_pattern_null_or_symbol",
    "swuquery_pattern_range",
    "swuquery_pattern_item",
    "swuquery_pattern_list",
    "swuquery_pattern_prefix",
    "swuquery_pattern_signbox",
    "swuquery_pattern_full",
]
