"""Time scale implementation for financial charts."""
from dataclasses import dataclass
from typing import Optional, List
import math
from .delegates import Delegate
from .time_data import (
    TimePointIndex,
    Coordinate,
    TimeScalePoint,
    RangeImpl,
    TimeScaleVisibleRange
)


@dataclass
class TimeMark:
    """Represents a tick mark on the horizontal (time) scale."""
    need_align_coordinate: bool
    coord: float
    label: str
    weight: int


@dataclass
class HorzScaleOptions:
    """Options for the time scale (horizontal scale)."""
    right_offset: float = 0
    right_offset_pixels: Optional[float] = None
    bar_spacing: float = 6
    min_bar_spacing: float = 0.5
    max_bar_spacing: float = 0
    fix_left_edge: bool = False
    fix_right_edge: bool = False
    lock_visible_time_range_on_resize: bool = False
    right_bar_stays_on_scroll: bool = False
    border_visible: bool = True
    visible: bool = True
    time_visible: bool = False
    seconds_visible: bool = True
    shift_visible_range_on_new_bar: bool = True
    allow_shift_visible_range_on_whitespace_replacement: bool = False
    ticks_visible: bool = False
    uniform_distribution: bool = False
    minimum_height: int = 0
    allow_bold_labels: bool = True
    ignore_whitespace_indices: bool = False


class TimeScale:
    """Implements the time scale for financial charts."""

    def __init__(self, model, options: HorzScaleOptions, horz_scale_behavior):
        """Initialize the time scale with options and behavior."""
        self._options = options
        self._model = model
        self._horz_scale_behavior = horz_scale_behavior

        self._width: float = 0
        self._base_index_or_null: Optional[TimePointIndex] = None
        self._right_offset: float = options.right_offset
        self._bar_spacing: float = options.bar_spacing
        self._points: List[TimeScalePoint] = []

        # Vispy-specific: We'll use a coordinate system that maps to screen pixels
        self._visible_range = TimeScaleVisibleRange.invalid()
        self._visible_range_invalidated: bool = True

        # Delegates for event system
        self._visible_bars_changed = Delegate()
        self._logical_range_changed = Delegate()
        self._options_applied = Delegate()

        # Caches
        self._time_marks_cache: Optional[List[TimeMark]] = None
        self._labels: List[TimeMark] = []

        # Initialize
        self._check_right_offset_pixels(options)

    def options(self) -> HorzScaleOptions:
        """Get the current time scale options."""
        return self._options

    def set_width(self, new_width: float):
        """Set the width of the time scale in pixels."""
        if not math.isfinite(new_width) or new_width <= 0:
            return

        if self._width == new_width:
            return

        old_width = self._width
        self._width = new_width
        self._visible_range_invalidated = True

        if self._options.lock_visible_time_range_on_resize and old_width != 0:
            # Recalculate bar spacing to maintain visible range
            new_bar_spacing = self._bar_spacing * new_width / old_width
            self._bar_spacing = new_bar_spacing

        self._correct_bar_spacing()
        self._correct_offset()

    def index_to_coordinate(self, index: TimePointIndex) -> Coordinate:
        """Convert a time point index to a pixel coordinate."""
        if self.is_empty() or not isinstance(index, int):
            return 0.0

        base_index = self.base_index()
        delta_from_right = base_index + self._right_offset - index
        coordinate_calc = (
            (delta_from_right + 0.5) * self._bar_spacing
        )
        coordinate = self._width - coordinate_calc - 1
        return coordinate

    def coordinate_to_index(self, x: Coordinate) -> TimePointIndex:
        """Convert a pixel coordinate to a time point index."""
        index = math.ceil(self._coordinate_to_float_index(x))
        return index

    def _coordinate_to_float_index(self, x: Coordinate) -> float:
        """Convert coordinate to float index with precision."""
        delta_from_right = self._right_offset_for_coordinate(x)
        base_index = self.base_index()
        index = base_index + self._right_offset - delta_from_right
        return round(index * 1000000) / 1000000

    def _right_offset_for_coordinate(self, x: Coordinate) -> float:
        """Calculate right offset for a given coordinate."""
        return (self._width - 1 - x) / self._bar_spacing

    def is_empty(self) -> bool:
        """Check if the time scale is empty."""
        return (
            self._width == 0 or
            len(self._points) == 0 or
            self._base_index_or_null is None
        )

    def base_index(self) -> TimePointIndex:
        """Get the base index for calculations."""
        return self._base_index_or_null or 0

    def visible_strict_range(self) -> Optional[RangeImpl[TimePointIndex]]:
        """Get the visible strict range."""
        self._update_visible_range()
        return self._visible_range.strict_range()

    def _update_visible_range(self):
        """Update the visible range if invalidated."""
        if not self._visible_range_invalidated:
            return

        self._visible_range_invalidated = False

        if self.is_empty():
            self._set_visible_range(TimeScaleVisibleRange.invalid())
            return

        base_index = self.base_index()
        new_bars_length = self._width / self._bar_spacing
        right_border = self._right_offset + base_index
        left_border = right_border - new_bars_length + 1

        logical_range = RangeImpl(left_border, right_border)
        self._set_visible_range(TimeScaleVisibleRange(logical_range))

    def _set_visible_range(self, new_visible_range: TimeScaleVisibleRange):
        """Set the visible range and fire events if changed."""
        old_visible_range = self._visible_range
        self._visible_range = new_visible_range

        # Fire events if ranges changed
        old_strict = (
            old_visible_range.strict_range()
            if old_visible_range else None
        )
        new_strict = new_visible_range.strict_range()

        if old_strict != new_strict:
            self._visible_bars_changed.fire()

        old_logical = (
            old_visible_range.logical_range()
            if old_visible_range else None
        )
        new_logical = new_visible_range.logical_range()

        if old_logical != new_logical:
            self._logical_range_changed.fire()

        self._time_marks_cache = None

    def _correct_bar_spacing(self):
        """Correct bar spacing to stay within min/max limits."""
        bar_spacing = self._clamp(
            self._bar_spacing,
            self._min_bar_spacing(),
            self._max_bar_spacing()
        )
        if self._bar_spacing != bar_spacing:
            self._bar_spacing = bar_spacing
            self._visible_range_invalidated = True

    def _min_bar_spacing(self) -> float:
        """Calculate the minimum allowed bar spacing."""
        if (
            self._options.fix_left_edge and
            self._options.fix_right_edge and
            len(self._points) != 0
        ):
            return self._width / len(self._points)
        return self._options.min_bar_spacing

    def _max_bar_spacing(self) -> float:
        """Calculate the maximum allowed bar spacing."""
        if self._options.max_bar_spacing > 0:
            return self._options.max_bar_spacing
        return self._width * 0.5

    def _correct_offset(self):
        """Correct offset to stay within data boundaries."""
        # Prevent scrolling past data boundaries
        min_right_offset = self._min_right_offset()
        if min_right_offset is not None and self._right_offset < min_right_offset:
            self._right_offset = min_right_offset
            self._visible_range_invalidated = True

        max_right_offset = self._max_right_offset()
        if self._right_offset > max_right_offset:
            self._right_offset = max_right_offset
            self._visible_range_invalidated = True

    def _min_right_offset(self) -> Optional[float]:
        """Calculate the minimum right offset."""
        first_index = self._first_index()
        base_index = self._base_index_or_null
        if first_index is None or base_index is None:
            return None

        bars_estimation = self._width / self._bar_spacing
        if not self._options.fix_left_edge:
            bars_estimation = min(2, len(self._points))

        offset_calc = first_index - base_index - 1
        total_offset = offset_calc + bars_estimation
        return total_offset

    def _max_right_offset(self) -> float:
        """Calculate the maximum right offset."""
        if self._options.fix_right_edge:
            return 0
        else:
            bars_in_view = self._width / self._bar_spacing
            min_bars = min(2, len(self._points))
            return bars_in_view - min_bars

    def _first_index(self) -> Optional[TimePointIndex]:
        """Get the first time point index."""
        return 0 if self._points else None

    def _last_index(self) -> Optional[TimePointIndex]:
        """Get the last time point index."""
        return len(self._points) - 1 if self._points else None

    def _clamp(self, value: float, min_val: float, max_val: float) -> float:
        """Clamp a value between min and max."""
        return max(min_val, min(value, max_val))

    def _check_right_offset_pixels(self, options):
        """Check and adjust right offset if pixels are specified."""
        if options.right_offset_pixels is not None:
            # This would call back to model - we'll implement this later
            pass

    # Vispy integration method
    def update_vispy_coordinates(self, vispy_canvas):
        """Update Vispy canvas based on current time scale state."""
        if self.is_empty():
            return

        visible_range = self.visible_strict_range()
        if visible_range:
            # Convert logical coordinates to Vispy's coordinate system
            left_idx = visible_range.left()
            right_idx = visible_range.right()
            self._update_vispy_viewport(vispy_canvas, left_idx, right_idx)

    def _update_vispy_viewport(self, vispy_canvas, left_idx: TimePointIndex,
                               right_idx: TimePointIndex):
        """Update Vispy's viewport to match the visible time range."""
        # Implementation depends on Vispy scene structure
        # Placeholder for future implementation
