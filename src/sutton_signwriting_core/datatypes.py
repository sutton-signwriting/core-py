"""
Data Types for Sutton SignWriting core functionality.
"""

from typing import (
    TypedDict,
    List,
    Union,
    Optional,
    Dict,
    NotRequired,
)

# Query-related types


class QuerySignboxSymbol(TypedDict):
    """A symbol in a signbox query."""

    symbol: str
    """A symbol identifier."""
    coord: Optional[List[int]]
    """An optional coordinate [x, y]."""


class QuerySignboxRange(TypedDict):
    """A symbol range in a signbox query."""

    range: List[str]
    """An array of two symbols defining the range [start, end]."""
    coord: Optional[List[int]]
    """An optional coordinate [x, y]."""


class QuerySignboxOr(TypedDict):
    """An OR group of symbols or ranges in a signbox query."""

    or_: List[Union[str, List[str]]]
    """An array of symbol strings and/or range arrays."""
    coord: Optional[List[int]]
    """An optional coordinate [x, y]."""


QuerySignboxElement = Union[QuerySignboxSymbol, QuerySignboxRange, QuerySignboxOr]


class QueryPrefix(TypedDict):
    """Prefix elements for a query."""

    required: bool
    """Whether the prefix is required."""
    parts: Optional[List[Union[str, List[str], List[Union[str, List[str]]]]]]
    """An object for prefix elements."""


class QueryObject(TypedDict):
    """
    Object of query elements with regular expression identification.
    """

    query: bool
    """Required true for query object."""
    prefix: NotRequired[Optional[QueryPrefix]]
    """An object for prefix elements."""
    signbox: NotRequired[Optional[List[QuerySignboxElement]]]
    """Array of objects for symbols, ranges, and list of symbols or ranges, with optional coordinates."""
    variance: NotRequired[Optional[int]]
    """Amount that x or y coordinates can vary and find a match, defaults to 20."""
    style: NotRequired[Optional[bool]]
    """Boolean value for including style string in matches."""


# Column and layout types


class ColumnPunctuation(TypedDict):
    """Punctuation options for columns."""

    spacing: Optional[bool]
    """Whether to add spacing for punctuation."""
    pad: Optional[int]
    """Padding for punctuation."""
    pull: Optional[bool]
    """Whether to pull punctuation closer."""


class StyleObject(TypedDict):
    """
    The elements of a style string.
    """

    colorize: Optional[bool]
    """Boolean to use standardized colors for symbol groups."""
    padding: Optional[int]
    """Integer value for padding around symbol or sign."""
    background: Optional[str]
    """CSS name or hex color for background."""
    detail: Optional[List[str]]
    """Array for CSS name or hex color for line and optional fill."""
    zoom: Optional[float]
    """Decimal value for zoom level."""
    detailsym: Optional[List[Dict[str, Union[int, List[str]]]]]
    """Custom colors for individual symbols: list of {index: int, detail: List[str]}."""
    classes: Optional[str]
    """List of class names separated with spaces used for SVG."""
    id: Optional[str]
    """ID name used for SVG."""


class ColumnOptions(TypedDict):
    """
    Options for column layout.
    """

    height: Optional[int]
    """The height of the columns."""
    width: Optional[int]
    """The widths of the columns."""
    offset: Optional[int]
    """The lane offset for left and right lanes."""
    pad: Optional[int]
    """Amount of padding before and after signs as well as at top, left, and right of columns."""
    margin: Optional[int]
    """Amount of space at bottom of column that is not available."""
    dynamic: Optional[bool]
    """Enables variable width columns."""
    background: Optional[str]
    """Background color for columns."""
    style: Optional[StyleObject]
    """An object of style options."""
    punctuation: Optional[ColumnPunctuation]
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
    zoom: float
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

# Symbol and sign types


class SymbolObject(TypedDict):
    """
    The elements of a symbol string.
    """

    symbol: Optional[str]
    """Symbol identifier."""
    coord: Optional[List[int]]
    """X, y coordinate."""
    style: Optional[str]
    """Style string."""


class SignSpatial(TypedDict):
    """A spatial symbol in a sign."""

    symbol: str
    """Symbol identifier."""
    coord: List[int]
    """Coordinate [x, y]."""


class SignObject(TypedDict):
    """
    The elements of a sign string.
    """

    sequence: Optional[List[str]]
    """Array of symbols."""
    box: Optional[str]
    """Signbox marker or lane."""
    max: Optional[List[int]]
    """Preprocessed x, y coordinate."""
    spatials: Optional[List[SignSpatial]]
    """Array of symbols with coordinates."""
    style: Optional[str]
    """Style string."""


__all__ = [
    "ColumnData",
    "ColumnOptions",
    "ColumnPunctuation",
    "ColumnSegment",
    "QueryObject",
    "QueryPrefix",
    "QuerySignboxElement",
    "QuerySignboxOr",
    "QuerySignboxRange",
    "QuerySignboxSymbol",
    "SegmentInfo",
    "SignObject",
    "SignSpatial",
    "StyleObject",
    "SymbolObject",
]
