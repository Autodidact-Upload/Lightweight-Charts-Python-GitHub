"""Price scale implementation for financial charts (vertical axis)."""
from dataclasses import dataclass
from typing import Optional, List, Callable, Any, Tuple
import math
from .delegates import Delegate
from .time_data import TimePointIndex, Coordinate, RangeImpl


@dataclass
class PriceScaleState:
    """Represents the state of the price scale."""
    auto_scale: bool
    is_inverted: bool
    mode: int


@dataclass
class PriceMark:
    """Represents a price mark on the vertical scale."""
    coord: Coordinate
    label: str
    logical: float


@dataclass
class PriceScaleMargins:
    """Defines margins of the price scale."""
    top: float  # Must be between 0 and 1
    bottom: float  # Must be between 0 and 1


@dataclass
class PriceScaleOptions:
    """Options for the price scale (vertical scale)."""
    auto_scale: bool = True
    mode: int = 0  # PriceScaleMode.Normal
    invert_scale: bool = False
    align_labels: bool = True
    scale_margins: PriceScaleMargins = None
    border_visible: bool = True
    border_color: str = '#2B2B43'
    text_color: Optional[str] = None
    entire_text_only: bool = False
    visible: bool = True
    ticks_visible: bool = False
    minimum_width: int = 0
    ensure_edge_tick_marks_visible: bool = False

    def __post_init__(self):
        if self.scale_margins is None:
            self.scale_margins = PriceScaleMargins(top=0.2, bottom=0.1)


class PriceRangeImpl:
    """Implements a price range with min and max values."""

    def __init__(self, min_value: float, max_value: float):
        self._min_value = min_value
        self._max_value = max_value

    def min_value(self) -> float:
        return self._min_value

    def max_value(self) -> float:
        return self._max_value

    def length(self) -> float:
        return self._max_value - self._min_value

    def isEmpty(self) -> bool:
        return self._min_value == self._max_value

    def equals(self, other: Optional['PriceRangeImpl']) -> bool:
        if other is None:
            return False
        return (self._min_value == other._min_value and 
                self._max_value == other._max_value)

    def clone(self) -> 'PriceRangeImpl':
        return PriceRangeImpl(self._min_value, self._max_value)

    def scale_around_center(self, coeff: float):
        """Scale the range around its center."""
        center = (self._min_value + self._max_value) / 2
        half_length = self.length() / 2
        new_half_length = half_length * coeff
        self._min_value = center - new_half_length
        self._max_value = center + new_half_length

    def shift(self, delta: float):
        """Shift the range by delta."""
        self._min_value += delta
        self._max_value += delta

    def merge(self, other: 'PriceRangeImpl') -> 'PriceRangeImpl':
        """Merge with another range."""
        return PriceRangeImpl(
            min(self._min_value, other._min_value),
            max(self._max_value, other._max_value)
        )


class PriceScale:
    """Implements the price scale for financial charts (vertical axis)."""

    # Price scale modes
    NORMAL = 0
    LOGARITHMIC = 1
    PERCENTAGE = 2
    INDEXED_TO_100 = 3

    def __init__(self, scale_id: str, options: PriceScaleOptions, layout_options: Any, 
                 localization_options: Any, color_parser: Any):
        """Initialize the price scale with options."""
        self._id = scale_id
        self._options = options
        self._layout_options = layout_options
        self._localization_options = localization_options
        self._color_parser = color_parser

        self._height: float = 0
        self._internal_height_cache: Optional[float] = None

        self._price_range: Optional[PriceRangeImpl] = None
        self._price_range_snapshot: Optional[PriceRangeImpl] = None
        self._invalidated_for_range = {'is_valid': False, 'visible_bars': None}

        self._is_custom_price_range: bool = False

        self._margin_above: float = 0
        self._margin_below: float = 0

        self._on_marks_changed = Delegate()
        self._mode_changed = Delegate()

        self._data_sources: List[Any] = []
        self._formatter_source: Optional[Any] = None
        self._cached_ordered_sources: Optional[List[Any]] = None

        self._marks_cache: Optional[Any] = None

        self._scale_start_point: Optional[float] = None
        self._scroll_start_point: Optional[float] = None

        # Initialize default margins
        self._invalidate_internal_height_cache()

    def id(self) -> str:
        """Get the price scale ID."""
        return self._id

    def options(self) -> PriceScaleOptions:
        """Get the current price scale options."""
        return self._options

    def apply_options(self, options: Any):
        """Apply new options to the price scale."""
        # Merge options logic would go here
        if hasattr(options, 'scale_margins') and options.scale_margins:
            margins = options.scale_margins
            if margins.top < 0 or margins.top > 1:
                raise ValueError(f"Invalid top margin - must be between 0 and 1, given={margins.top}")
            if margins.bottom < 0 or margins.bottom > 1:
                raise ValueError(f"Invalid bottom margin - must be between 0 and 1, given={margins.bottom}")
            if margins.top + margins.bottom > 1:
                raise ValueError(f"Invalid margins - sum must be less than 1, given={margins.top + margins.bottom}")

            self._invalidate_internal_height_cache()
            self._marks_cache = None

        if hasattr(options, 'mode'):
            self.set_mode({'mode': options.mode})

    def is_auto_scale(self) -> bool:
        """Check if auto-scaling is enabled."""
        return self._options.auto_scale

    def is_custom_price_range(self) -> bool:
        """Check if using a custom price range."""
        return self._is_custom_price_range

    def is_log(self) -> bool:
        """Check if in logarithmic mode."""
        return self._options.mode == self.LOGARITHMIC

    def is_percentage(self) -> bool:
        """Check if in percentage mode."""
        return self._options.mode == self.PERCENTAGE

    def is_indexed_to_100(self) -> bool:
        """Check if in indexed to 100 mode."""
        return self._options.mode == self.INDEXED_TO_100

    def mode(self) -> PriceScaleState:
        """Get the current price scale mode state."""
        return PriceScaleState(
            auto_scale=self._options.auto_scale,
            is_inverted=self._options.invert_scale,
            mode=self._options.mode
        )

    def set_mode(self, new_mode: Any):
        """Set the price scale mode."""
        # Mode change logic would go here
        old_mode = self.mode()
        
        if hasattr(new_mode, 'auto_scale'):
            self._options.auto_scale = new_mode.auto_scale
            
        if hasattr(new_mode, 'mode'):
            self._options.mode = new_mode.mode
            if new_mode.mode in [self.PERCENTAGE, self.INDEXED_TO_100]:
                self._options.auto_scale = True
            self._invalidated_for_range['is_valid'] = False

        # Fire mode changed event
        self._mode_changed.fire(old_mode, self.mode())

    def mode_changed(self):
        """Get the mode changed delegate."""
        return self._mode_changed

    def font_size(self) -> float:
        """Get the font size from layout options."""
        return getattr(self._layout_options, 'font_size', 12)

    def height(self) -> float:
        """Get the height of the price scale."""
        return self._height

    def set_height(self, value: float):
        """Set the height of the price scale."""
        if self._height == value:
            return

        self._height = value
        self._invalidate_internal_height_cache()
        self._marks_cache = None

    def internal_height(self) -> float:
        """Get the internal height (excluding margins)."""
        if self._internal_height_cache is not None:
            return self._internal_height_cache

        res = self.height() - self._top_margin_px() - self._bottom_margin_px()
        self._internal_height_cache = res
        return res

    def price_range(self) -> Optional[PriceRangeImpl]:
        """Get the current price range."""
        self._make_sure_it_is_valid()
        return self._price_range

    def set_price_range(self, new_price_range: Optional[PriceRangeImpl], is_force_set_value: bool = False):
        """Set the price range."""
        old_price_range = self._price_range

        if (not is_force_set_value and
            not (old_price_range is None and new_price_range is not None) and
            (old_price_range is None or old_price_range.equals(new_price_range))):
            return

        self._marks_cache = None
        self._price_range = new_price_range

    def set_custom_price_range(self, new_price_range: Optional[PriceRangeImpl]):
        """Set a custom price range."""
        self.set_price_range(new_price_range)
        self._toggle_custom_price_range(new_price_range is not None)

    def is_empty(self) -> bool:
        """Check if the price scale is empty."""
        self._make_sure_it_is_valid()
        return (self._height == 0 or 
                self._price_range is None or 
                self._price_range.isEmpty())

    def is_inverted(self) -> bool:
        """Check if the scale is inverted."""
        return self._options.invert_scale

    def inverted_coordinate(self, coordinate: float) -> float:
        """Invert a coordinate based on scale inversion."""
        return coordinate if self.is_inverted() else self.height() - 1 - coordinate

    def price_to_coordinate(self, price: float, base_value: float) -> Coordinate:
        """Convert a price to a pixel coordinate."""
        if self.is_percentage():
            price = self._to_percent(price, base_value)
        elif self.is_indexed_to_100():
            price = self._to_indexed_to_100(price, base_value)

        return self._logical_to_coordinate(price, base_value)

    def coordinate_to_price(self, coordinate: Coordinate, base_value: float) -> float:
        """Convert a pixel coordinate to a price."""
        logical = self._coordinate_to_logical(coordinate, base_value)
        return self._logical_to_price(logical, base_value)

    def data_sources(self):
        """Get the data sources attached to this scale."""
        return self._data_sources

    def add_data_source(self, source: Any):
        """Add a data source to the price scale."""
        if source in self._data_sources:
            return

        self._data_sources.append(source)
        self._invalidate_sources_cache()

    def remove_data_source(self, source: Any):
        """Remove a data source from the price scale."""
        if source not in self._data_sources:
            raise ValueError('Source is not attached to scale')

        self._data_sources.remove(source)

        if len(self._data_sources) == 0:
            self.set_mode({'auto_scale': True})
            self.set_price_range(None)

        self._invalidate_sources_cache()

    def first_value(self) -> Optional[float]:
        """Get the first value from data sources."""
        # TODO: Implement proper first value logic
        return None

    def marks(self) -> List[PriceMark]:
        """Get the price marks for the scale."""
        # Placeholder for mark generation logic
        return []

    def on_marks_changed(self):
        """Get the marks changed delegate."""
        return self._on_marks_changed

    def recalculate_price_range(self, visible_bars: RangeImpl[TimePointIndex]):
        """Recalculate the price range for visible bars."""
        self._invalidated_for_range = {
            'visible_bars': visible_bars,
            'is_valid': False,
        }

    # Private methods
    def _toggle_custom_price_range(self, value: bool):
        self._is_custom_price_range = value

    def _top_margin_px(self) -> float:
        if self.is_inverted():
            return (self._options.scale_margins.bottom * self.height() + 
                    self._margin_below)
        else:
            return (self._options.scale_margins.top * self.height() + 
                    self._margin_above)

    def _bottom_margin_px(self) -> float:
        if self.is_inverted():
            return (self._options.scale_margins.top * self.height() + 
                    self._margin_above)
        else:
            return (self._options.scale_margins.bottom * self.height() + 
                    self._margin_below)

    def _make_sure_it_is_valid(self):
        if not self._invalidated_for_range['is_valid']:
            self._invalidated_for_range['is_valid'] = True
            self._recalculate_price_range_impl()

    def _invalidate_internal_height_cache(self):
        self._internal_height_cache = None

    def _logical_to_coordinate(self, logical: float, base_value: float) -> Coordinate:
        self._make_sure_it_is_valid()
        if self.is_empty():
            return 0.0

        # Handle logarithmic transformation if needed
        # logical = self._to_log(logical) if self.is_log() else logical
        
        range_impl = self.price_range()
        if range_impl is None:
            return 0.0

        inv_coordinate = (self._bottom_margin_px() +
            (self.internal_height() - 1) * (logical - range_impl.min_value()) / 
            range_impl.length())
        coordinate = self.inverted_coordinate(inv_coordinate)
        return coordinate

    def _coordinate_to_logical(self, coordinate: float, base_value: float) -> float:
        self._make_sure_it_is_valid()
        if self.is_empty():
            return 0.0

        inv_coordinate = self.inverted_coordinate(coordinate)
        range_impl = self.price_range()
        if range_impl is None:
            return 0.0

        logical = (range_impl.min_value() + range_impl.length() *
            ((inv_coordinate - self._bottom_margin_px()) / 
             (self.internal_height() - 1)))
        # Handle logarithmic transformation if needed
        # return self._from_log(logical) if self.is_log() else logical
        return logical

    def _logical_to_price(self, logical: float, base_value: float) -> float:
        value = logical
        if self.is_percentage():
            value = self._from_percent(value, base_value)
        elif self.is_indexed_to_100():
            value = self._from_indexed_to_100(value, base_value)
        return value

    def _recalculate_price_range_impl(self):
        """Recalculate the price range implementation."""
        if self.is_custom_price_range() and not self.is_auto_scale():
            return

        visible_bars = self._invalidated_for_range['visible_bars']
        if visible_bars is None:
            return

        # Placeholder for actual price range calculation
        # This would iterate through data sources and calculate ranges
        price_range = PriceRangeImpl(-0.5, 0.5)  # Default range
        
        self.set_price_range(price_range)

    def _to_percent(self, price: float, base_value: float) -> float:
        """Convert price to percentage."""
        return ((price - base_value) / base_value) * 100

    def _from_percent(self, percent: float, base_value: float) -> float:
        """Convert percentage back to price."""
        return base_value * (1 + percent / 100)

    def _to_indexed_to_100(self, price: float, base_value: float) -> float:
        """Convert price to indexed to 100 format."""
        return (price / base_value) * 100

    def _from_indexed_to_100(self, indexed: float, base_value: float) -> float:
        """Convert indexed to 100 back to price."""
        return (indexed / 100) * base_value

    def _invalidate_sources_cache(self):
        self._cached_ordered_sources = None