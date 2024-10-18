"""Init file for the soap client."""

from collections.abc import Callable
from datetime import datetime, time
from typing import Any, TypeVar

from dateutil import parser

T = TypeVar("T")


def from_str(x: Any) -> str:
    """Get a string from an object."""
    return x


def from_datetime(x: Any) -> datetime:
    """Get a datetime from an object."""
    return parser.parse(x)


def from_time(x: Any) -> time:
    """Get a datetime from an object."""
    return from_datetime(x).time()


def from_float(x: Any) -> float:
    """Get a float from an object."""
    return float(from_str(x))


def from_int(x: Any) -> int:
    """Get an int from an object."""
    return int(from_str(x))


def from_bool(x: Any) -> bool:
    """Get a bool from an object."""
    string = from_str(x)
    return string.startswith("Y")


def from_list(f: Callable[[Any], T], x: Any) -> list[T]:
    """Get a list."""
    return [f(y) for y in x]
