"""
Data Types for Sutton SignWriting core functionality.
"""

from typing import (
    Dict,
    TypedDict,
    List,
    Union,
    NotRequired,
)

# Query-related types


class QuerySignboxSymbol(TypedDict):
    """A symbol in a signbox query."""

    symbol: str
    """A symbol identifier."""
    coord: NotRequired[List[int]]
    """An optional coordinate [x, y]."""


class QuerySignboxRange(TypedDict):
    """A symbol range in a signbox query."""

    range: List[str]
    """An array of two symbols defining the range [start, end]."""
    coord: NotRequired[List[int]]
    """An optional coordinate [x, y]."""


class QuerySignboxOr(TypedDict):
    """An OR group of symbols or ranges in a signbox query."""

    or_list: List[Union[str, List[str]]]
    """An array of symbol strings and/or range arrays."""
    coord: NotRequired[List[int]]
    """An optional coordinate [x, y]."""


QuerySignboxElement = Union[QuerySignboxSymbol, QuerySignboxRange, QuerySignboxOr]
"""A signbox query element as a symbol, range, or an OR group of symbols and ranges."""


QueryPrefixSymbol = str
"""A symbol identifier in a prefix query."""

QueryPrefixRange = List[str]
"""A symbol range in a prefix query."""

QueryPrefixOr = List[Union[str, List[str]]]
"""An OR group of symbols or ranges in a prefix query."""

QueryPrefixElement = Union[QueryPrefixSymbol, QueryPrefixRange, QueryPrefixOr]
"""A prefix query element as a :py:data:`.QueryPrefixSymbol`, :py:data:`.QueryPrefixRange`, or :py:data:`.QueryPrefixOr`."""


class QueryPrefix(TypedDict):
    """Prefix elements for a query."""

    required: bool
    """Whether the prefix is required."""
    parts: NotRequired[List[QueryPrefixElement]]
    """A list of symbols, ranges, or OR groups."""


class QueryObject(TypedDict):
    """
    Object of query elements with regular expression identification.
    """

    query: bool
    """Required true for query object."""
    prefix: NotRequired[QueryPrefix]
    """An object for prefix elements."""
    signbox: NotRequired[List[QuerySignboxElement]]
    """Array of objects for symbols, ranges, and list of symbols or ranges, with optional coordinates."""
    variance: NotRequired[int]
    """Amount that x or y coordinates can vary and find a match, defaults to 20."""
    style: NotRequired[bool]
    """Boolean value for including style string in matches."""


# Column and layout types


class ColumnPunctuation(TypedDict):
    """Punctuation options for columns."""

    spacing: NotRequired[bool]
    """Whether to add spacing for punctuation."""
    pad: NotRequired[int]
    """Padding for punctuation."""
    pull: NotRequired[bool]
    """Whether to pull punctuation closer."""


class DetailSym(TypedDict):
    """
    A symbol-specific style configuration for custom colors.
    """

    index: int
    """The index of the symbol."""
    detail: List[str]
    """Array of CSS names or hex colors for line and optional fill."""


class StyleObject(TypedDict):
    """
    The elements of a style string.
    """

    colorize: NotRequired[bool]
    """Boolean to use standardized colors for symbol groups."""
    padding: NotRequired[int]
    """Integer value for padding around symbol or sign."""
    background: NotRequired[str]
    """CSS name or hex color for background."""
    detail: NotRequired[List[str]]
    """Array for CSS name or hex color for line and optional fill."""
    zoom: NotRequired[Union[int, float, str]]
    """Decimal value for zoom level."""
    detailsym: NotRequired[List[DetailSym]]
    """Custom colors for individual symbols: list of {index: int, detail: List[str]}."""
    classes: NotRequired[str]
    """List of class names separated with spaces used for SVG."""
    id: NotRequired[str]
    """ID name used for SVG."""


class ColumnOptions(TypedDict):
    """
    Options for column layout.
    """

    height: NotRequired[int]
    """The height of the columns."""
    width: NotRequired[int]
    """The widths of the columns."""
    offset: NotRequired[int]
    """The lane offset for left and right lanes."""
    pad: NotRequired[int]
    """Amount of padding before and after signs as well as at top, left, and right of columns."""
    margin: NotRequired[int]
    """Amount of space at bottom of column that is not available."""
    dynamic: NotRequired[bool]
    """Enables variable width columns."""
    background: NotRequired[str]
    """Background color for columns."""
    style: NotRequired[StyleObject]
    """An object of style options."""
    punctuation: NotRequired[ColumnPunctuation]
    """An object of punctuation options."""


class SegmentInfo(TypedDict):
    """
    Information about a text segment.
    """

    minX: int
    """The min x value within the segment."""
    minY: int
    """The min y value within the segment."""
    width: int
    """The width of the text segment."""
    height: int
    """The height of the text segment."""
    lane: int
    """Left as -1, Middle as 0, Right as 1."""
    padding: int
    """The padding of the text segment affects colored background."""
    segment: str
    """'sign' or 'symbol'."""
    zoom: Union[int, float, str]
    """The zoom size of the segment."""


class ColumnSegment(SegmentInfo):
    """A segment in a column layout (extends SegmentInfo with position and text)."""

    x: int
    """The x position in the column."""
    y: int
    """The y position in the column."""
    text: str
    """The text of the sign or symbol with optional style string."""


ColumnData = List[ColumnSegment]


class ColumnsResult(TypedDict):
    """
    The result of the columns functions, containing column layout data.
    """

    options: NotRequired[ColumnOptions]
    """Column layout options."""
    widths: NotRequired[List[int]]
    """Widths of each column."""
    columns: NotRequired[List[List[ColumnSegment]]]
    """Array of columns, each containing an array of segments."""


class SymbolObject(TypedDict):
    """
    The elements of a symbol string.
    """

    symbol: NotRequired[str]
    """Symbol identifier."""
    coord: NotRequired[List[int]]
    """X, y coordinate."""
    style: NotRequired[str]
    """Style string."""


class SignSpatial(TypedDict):
    """A spatial symbol in a sign."""

    symbol: str
    """Symbol identifier."""
    coord: List[int]
    """Coordinate [x, y]."""
    detail: NotRequired[List[str]]
    """Array for CSS name or hex color for line and optional fill."""


class SignObject(TypedDict):
    """
    The elements of a sign string.
    """

    sequence: NotRequired[List[str]]
    """Array of symbols."""
    box: NotRequired[str]
    """Signbox marker or lane."""
    max: NotRequired[List[int]]
    """Preprocessed x, y coordinate."""
    spatials: NotRequired[List[SignSpatial]]
    """Array of symbols with coordinates."""
    style: NotRequired[str]
    """Style string."""


class SpecialToken(TypedDict):
    index: int
    name: str
    value: str


class TokenizerMappings(TypedDict):
    i2s: Dict[int, str]
    s2i: Dict[str, int]


__all__ = [
    "ColumnData",
    "ColumnOptions",
    "ColumnPunctuation",
    "ColumnSegment",
    "ColumnsResult",
    "QueryObject",
    "QueryPrefixSymbol",
    "QueryPrefixRange",
    "QueryPrefixOr",
    "QueryPrefixElement",
    "QueryPrefix",
    "QuerySignboxElement",
    "QuerySignboxOr",
    "QuerySignboxRange",
    "QuerySignboxSymbol",
    "SegmentInfo",
    "SignObject",
    "SignSpatial",
    "DetailSym",
    "StyleObject",
    "SymbolObject",
    "SpecialToken",
    "TokenizerMappings",
]
