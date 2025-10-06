"""Type definitions and data structures for time scale functionality."""
from dataclasses import dataclass
from typing import Generic, TypeVar, Optional, Any
import math

# Type variables for generics
T = TypeVar('T')

# Type definitions matching TypeScript
TimePointIndex = int
Logical = float
Coordinate = float


@dataclass
class LogicalRange:
    """Represents a logical range with from and to values."""
    from_val: Logical
    to_val: Logical


@dataclass
class TimePointsRange:
    """Represents a time points range with from and to TimeScalePoints."""
    from_val: Any  # TimeScalePoint
    to_val: Any   # TimeScalePoint


@dataclass
class TimeScalePoint:
    """Represents a point on the time scale."""
    time: Any
    original_time: Any


class RangeImpl(Generic[T]):
    """Implements a generic range with left and right boundaries."""

    def __init__(self, left: T, right: T):
        """Initialize range with left and right boundaries."""
        self._left = left
        self._right = right

    def left(self) -> T:
        """Get the left boundary."""
        return self._left

    def right(self) -> T:
        """Get the right boundary."""
        return self._right

    def count(self) -> int:
        """Calculate the count of elements in the range."""
        return self._right - self._left + 1


class TimeScaleVisibleRange:
    """Manages the visible range for time scale calculations."""

    @staticmethod
    def invalid():
        """Create an invalid time scale visible range."""
        return TimeScaleVisibleRange()

    def __init__(self, logical_range: Optional[RangeImpl[Logical]] = None):
        """Initialize with an optional logical range."""
        self._logical_range = logical_range
        self._strict_range = None
        if logical_range:
            self._strict_range = RangeImpl(
                int(math.floor(logical_range.left())),
                int(math.floor(logical_range.right()))
            )

    def strict_range(self) -> Optional[RangeImpl[TimePointIndex]]:
        """Get the strict range as TimePointIndex."""
        return self._strict_range

    def logical_range(self) -> Optional[RangeImpl[Logical]]:
        """Get the logical range."""
        return self._logical_range
