"""
Data Types for Sutton SignWriting core functionality.
"""

from typing import (
    Dict,
    List,
    Union,
    NotRequired,
)

from typing_extensions import TypedDict


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
    """Value for specific zoom level or the letter 'x' for expandable."""
    detailsym: NotRequired[List[DetailSym]]
    """Custom colors for individual symbols"""
    classes: NotRequired[str]
    """List of class names separated with spaces used for SVG."""
    id: NotRequired[str]
    """ID name used for SVG."""


class ColumnPunctuation(TypedDict):
    """Punctuation options for columns."""

    spacing: NotRequired[bool]
    """Whether to add spacing for punctuation."""
    pad: NotRequired[int]
    """Padding for punctuation."""
    pull: NotRequired[bool]
    """Whether to pull punctuation closer."""


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


QueryPrefixSymbol = str
"""A symbol identifier in a prefix query.

alias of :class:`str`
"""

QueryPrefixRange = List[str]
"""An array of two symbols defining the range [start, end]."""

QueryPrefixOr = List[Union[QueryPrefixSymbol, QueryPrefixRange]]
"""An OR group of symbols or ranges in a prefix query.

- element 0: Must be the string 'or_list'
- elements 1+: :class:`QueryPrefixSymbol` or :class:`QueryPrefixRange`
"""

QueryPrefixElement = Union[QueryPrefixSymbol, QueryPrefixRange, QueryPrefixOr]
"""A prefix query element as a symbol, range, or an OR group of symbols and ranges.

alias of :class:`QueryPrefixSymbol` | :class:`QueryPrefixRange` | :class:`QueryPrefixOr`
"""


class QueryPrefix(TypedDict):
    """Prefix elements for a query."""

    required: bool
    """Whether the prefix is required."""
    parts: NotRequired[List[QueryPrefixElement]]
    """A list of :class:`QueryPrefixElement` items."""


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

    or_list: List[Union[QuerySignboxSymbol, QuerySignboxRange]]
    """An array of symbol strings and/or range arrays."""
    coord: NotRequired[List[int]]
    """An optional coordinate [x, y]."""


QuerySignboxElement = Union[QuerySignboxSymbol, QuerySignboxRange, QuerySignboxOr]
"""A signbox query element as a symbol, range, or an OR group of symbols and ranges."""


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


class SpecialToken(TypedDict):
    """
    Configuration for a special token in the FSW tokenizer vocabulary.
    """

    index: int
    """Unique integer index for this token in the vocabulary."""
    name: str
    """Human-readable identifier for the token."""
    value: str
    """Literal string representation of the token."""


class TokenizerMappings(TypedDict):
    """
    Bidirectional mappings for token indices and strings in the FSW tokenizer.
    """

    i2s: Dict[int, str]
    """Mapping from integer indices to token strings."""
    s2i: Dict[str, int]
    """Mapping from token strings to integer indices."""


__all__ = [
    "SymbolObject",
    "SignSpatial",
    "SignObject",
    "DetailSym",
    "StyleObject",
    "ColumnPunctuation",
    "ColumnOptions",
    "SegmentInfo",
    "ColumnSegment",
    "ColumnsResult",
    "QueryPrefixSymbol",
    "QueryPrefixRange",
    "QueryPrefixOr",
    "QueryPrefixElement",
    "QueryPrefix",
    "QuerySignboxSymbol",
    "QuerySignboxRange",
    "QuerySignboxOr",
    "QuerySignboxElement",
    "QueryObject",
    "SpecialToken",
    "TokenizerMappings",
]
