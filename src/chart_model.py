"""Chart model implementation - the central coordinator for chart components."""
from dataclasses import dataclass
from typing import Optional, List, Any, Callable, Dict
from .delegates import Delegate
from .time_data import TimePointIndex, Coordinate, Point, LogicalRange
from .time_scale import TimeScale, HorzScaleOptions
from .price_scale import PriceScale, PriceScaleOptions, PriceScaleOnPane


@dataclass
class HandleScrollOptions:
    """Options for how the chart is scrolled by mouse and touch gestures."""
    mouse_wheel: bool = True
    pressed_mouse_move: bool = True
    horz_touch_drag: bool = True
    vert_touch_drag: bool = True


@dataclass
class HandleScaleOptions:
    """Options for how the chart is scaled by mouse and touch gestures."""
    mouse_wheel: bool = True
    pinch: bool = True
    axis_pressed_mouse_move: Any = None
    axis_double_click_reset: Any = None


@dataclass
class CrosshairOptions:
    """Options for the crosshair display."""
    # Crosshair configuration would go here
    pass


@dataclass
class GridOptions:
    """Options for the grid display."""
    # Grid configuration would go here
    pass


@dataclass
class ChartOptions:
    """Main chart options configuration."""
    width: int = 0
    height: int = 0
    auto_size: bool = False
    layout: Any = None
    left_price_scale: PriceScaleOptions = None
    right_price_scale: PriceScaleOptions = None
    overlay_price_scales: Any = None
    time_scale: HorzScaleOptions = None
    crosshair: CrosshairOptions = None
    grid: GridOptions = None
    handle_scroll: HandleScrollOptions = None
    handle_scale: HandleScaleOptions = None
    kinetic_scroll: Any = None
    tracking_mode: Any = None
    localization: Any = None
    add_default_pane: bool = True

    def __post_init__(self):
        if self.left_price_scale is None:
            self.left_price_scale = PriceScaleOptions()
        if self.right_price_scale is None:
            self.right_price_scale = PriceScaleOptions()
        if self.time_scale is None:
            self.time_scale = HorzScaleOptions()
        if self.crosshair is None:
            self.crosshair = CrosshairOptions()
        if self.grid is None:
            self.grid = GridOptions()
        if self.handle_scroll is None:
            self.handle_scroll = HandleScrollOptions()
        if self.handle_scale is None:
            self.handle_scale = HandleScaleOptions()


class Crosshair:
    """Handles crosshair positioning and display."""

    def __init__(self, model: 'ChartModel', options: CrosshairOptions):
        self._model = model
        self._options = options
        self._origin_x: Optional[Coordinate] = None
        self._origin_y: Optional[Coordinate] = None
        self._pane: Optional[Any] = None
        self._index: Optional[TimePointIndex] = None
        self._price: Optional[float] = None

    def save_origin_coord(self, x: Coordinate, y: Coordinate):
        """Save the original crosshair coordinates."""
        self._origin_x = x
        self._origin_y = y

    def origin_coord_x(self) -> Optional[Coordinate]:
        """Get the original X coordinate."""
        return self._origin_x

    def origin_coord_y(self) -> Optional[Coordinate]:
        """Get the original Y coordinate."""
        return self._origin_y

    def set_position(self, index: TimePointIndex, price: float, pane: Any):
        """Set the crosshair position."""
        self._index = index
        self._price = price
        self._pane = pane

    def clear_position(self):
        """Clear the crosshair position."""
        self._index = None
        self._price = None
        self._pane = None
        self._origin_x = None
        self._origin_y = None

    def pane(self) -> Optional[Any]:
        """Get the current pane."""
        return self._pane

    def applied_index(self) -> Optional[TimePointIndex]:
        """Get the applied time index."""
        return self._index

    def update_all_views(self):
        """Update all crosshair views."""
        # Would update crosshair visual representations
        pass


class Magnet:
    """Handles magnetic alignment for crosshair positioning."""

    def __init__(self, options: CrosshairOptions):
        self._options = options

    def align(self, price: float, index: TimePointIndex, pane: Any) -> float:
        """Align price to magnetic points."""
        # Placeholder for magnetic alignment logic
        return price


class Pane:
    """Represents a chart pane containing price scales and series."""

    def __init__(self, time_scale: TimeScale, model: 'ChartModel'):
        self._time_scale = time_scale
        self._model = model
        self._width: float = 0
        self._height: float = 0
        self._stretch_factor: float = 1.0
        self._data_sources: List[Any] = []
        self._price_scales: Dict[str, PriceScale] = {}

    def set_width(self, width: float):
        """Set the pane width."""
        self._width = width

    def set_height(self, height: float):
        """Set the pane height."""
        self._height = height

    def height(self) -> float:
        """Get the pane height."""
        return self._height

    def set_stretch_factor(self, factor: float):
        """Set the stretch factor for pane sizing."""
        self._stretch_factor = factor

    def stretch_factor(self) -> float:
        """Get the stretch factor."""
        return self._stretch_factor

    def price_scale_by_id(self, price_scale_id: str) -> Optional[PriceScale]:
        """Get a price scale by its ID."""
        return self._price_scales.get(price_scale_id)

    def default_price_scale(self) -> PriceScale:
        """Get the default price scale for this pane."""
        # For now, return the first price scale or create one
        if not self._price_scales:
            # Create a default price scale
            default_scale = PriceScale(
                "right", 
                PriceScaleOptions(), 
                self._model.options().layout,
                self._model.options().localization,
                None  # color_parser would go here
            )
            self._price_scales["right"] = default_scale
        return next(iter(self._price_scales.values()))

    def add_data_source(self, source: Any, price_scale_id: str, preserve: bool = False):
        """Add a data source to this pane."""
        self._data_sources.append(source)
        # Would associate with price scale

    def remove_data_source(self, source: Any, preserve: bool = False):
        """Remove a data source from this pane."""
        if source in self._data_sources:
            self._data_sources.remove(source)

    def data_sources(self) -> List[Any]:
        """Get all data sources in this pane."""
        return self._data_sources.copy()

    def ordered_sources(self) -> List[Any]:
        """Get ordered data sources."""
        return self._data_sources.copy()

    def series(self) -> List[Any]:
        """Get series in this pane."""
        return [src for src in self._data_sources if hasattr(src, 'price_line')]

    def apply_scale_options(self, options: Any):
        """Apply scale options to this pane."""
        # Would apply options to price scales
        pass

    def recalculate(self):
        """Recalculate pane layout and scales."""
        # Would recalculate price scales and series
        pass

    def start_scale_price(self, price_scale: PriceScale, x: float):
        """Start scaling a price scale."""
        price_scale.start_scale(x)

    def scale_price_to(self, price_scale: PriceScale, x: float):
        """Scale price scale to position."""
        price_scale.scale_to(x)

    def end_scale_price(self, price_scale: PriceScale):
        """End price scale scaling."""
        price_scale.end_scale()

    def start_scroll_price(self, price_scale: PriceScale, x: float):
        """Start scrolling a price scale."""
        if not price_scale.is_auto_scale():
            price_scale.start_scroll(x)

    def scroll_price_to(self, price_scale: PriceScale, x: float):
        """Scroll price scale to position."""
        if not price_scale.is_auto_scale():
            price_scale.scroll_to(x)

    def end_scroll_price(self, price_scale: PriceScale):
        """End price scale scrolling."""
        if not price_scale.is_auto_scale():
            price_scale.end_scroll()

    def reset_price_scale(self, price_scale: PriceScale):
        """Reset price scale to auto-scale."""
        price_scale.set_mode({'auto_scale': True})

    def preserve_empty_pane(self) -> bool:
        """Check if empty pane should be preserved."""
        return len(self._data_sources) > 0

    def grid(self) -> Any:
        """Get the grid for this pane."""
        # Would return grid object
        return None


class ChartModel:
    """The central chart model coordinating time scale, price scales, and panes."""

    def __init__(self, invalidate_handler: Callable, options: ChartOptions, horz_scale_behavior: Any):
        self._invalidate_handler = invalidate_handler
        self._options = options
        self._horz_scale_behavior = horz_scale_behavior

        # Core components
        self._time_scale = TimeScale(self, options.time_scale, horz_scale_behavior)
        self._crosshair = Crosshair(self, options.crosshair)
        self._magnet = Magnet(options.crosshair)

        # Collections
        self._panes: List[Pane] = []
        self._series: List[Any] = []

        # State
        self._width: float = 0
        self._hovered_source: Optional[Any] = None

        # Events
        self._price_scales_options_changed = Delegate()
        self._crosshair_moved = Delegate()

        # Initialize with default pane if requested
        if options.add_default_pane:
            default_pane = self._get_or_create_pane(0)
            default_pane.set_stretch_factor(2.0)  # DEFAULT_STRETCH_FACTOR * 2

    def options(self) -> ChartOptions:
        """Get the chart options."""
        return self._options

    def apply_options(self, options: Any):
        """Apply new chart options."""
        # Merge options logic would go here
        if hasattr(options, 'time_scale'):
            self._time_scale.apply_options(options.time_scale)

        self.full_update()

    def time_scale(self) -> TimeScale:
        """Get the time scale."""
        return self._time_scale

    def panes(self) -> List[Pane]:
        """Get all panes."""
        return self._panes.copy()

    def crosshair_source(self) -> Crosshair:
        """Get the crosshair."""
        return self._crosshair

    def crosshair_moved(self):
        """Get the crosshair moved delegate."""
        return self._crosshair_moved

    def set_width(self, width: float):
        """Set the chart width."""
        self._width = width
        self._time_scale.set_width(width)
        for pane in self._panes:
            pane.set_width(width)
        self.recalculate_all_panes()

    def set_pane_height(self, pane: Pane, height: float):
        """Set a pane's height."""
        pane.set_height(height)
        self.recalculate_all_panes()

    def full_update(self):
        """Perform a full chart update."""
        self._invalidate(self._create_invalidate_mask('full'))

    def light_update(self):
        """Perform a light chart update."""
        self._invalidate(self._create_invalidate_mask('light'))

    def cursor_update(self):
        """Update cursor only."""
        self._invalidate(self._create_invalidate_mask('cursor'))

    def update_source(self, source: Any):
        """Update a specific data source."""
        self._invalidate(self._create_invalidate_mask('light'))

    def hovered_source(self) -> Optional[Any]:
        """Get the currently hovered source."""
        return self._hovered_source

    def set_hovered_source(self, source: Optional[Any]):
        """Set the hovered source."""
        self._hovered_source = source

    def recalculate_pane(self, pane: Optional[Pane]):
        """Recalculate a specific pane."""
        if pane is not None:
            pane.recalculate()

    def recalculate_all_panes(self):
        """Recalculate all panes."""
        for pane in self._panes:
            pane.recalculate()
        self.update_crosshair()

    def update_crosshair(self):
        """Update the crosshair position."""
        pane = self._crosshair.pane()
        if pane is not None:
            x = self._crosshair.origin_coord_x()
            y = self._crosshair.origin_coord_y()
            if x is not None and y is not None:
                self.set_and_save_current_position(x, y, None, pane)

        self._crosshair.update_all_views()

    def set_and_save_current_position(self, x: Coordinate, y: Coordinate, 
                                    event: Optional[Any], pane: Pane, skip_event: bool = False):
        """Set and save the current crosshair position."""
        self._crosshair.save_origin_coord(x, y)
        
        index = self._time_scale.coordinate_to_index(x, True)
        
        # Constrain index to visible range
        visible_bars = self._time_scale.visible_strict_range()
        if visible_bars is not None:
            index = max(visible_bars.left(), min(index, visible_bars.right()))

        price_scale = pane.default_price_scale()
        first_value = price_scale.first_value()
        price = float('nan')
        if first_value is not None:
            price = price_scale.coordinate_to_price(y, first_value)
        
        # Apply magnetic alignment
        price = self._magnet.align(price, index, pane)

        self._crosshair.set_position(index, price, pane)
        self.cursor_update()

        if not skip_event:
            self._crosshair_moved.fire(self._crosshair.applied_index(), Point(x, y), event)

    def clear_current_position(self, skip_event: bool = False):
        """Clear the current crosshair position."""
        self._crosshair.clear_position()
        self.cursor_update()
        if not skip_event:
            self._crosshair_moved.fire(None, None, None)

    def start_scale_time(self, position: Coordinate):
        """Start scaling the time scale."""
        self._time_scale.start_scale(position)

    def scale_time_to(self, x: Coordinate):
        """Scale the time scale to position."""
        self._time_scale.scale_to(x)
        self.recalculate_all_panes()

    def end_scale_time(self):
        """End time scale scaling."""
        self._time_scale.end_scale()
        self.light_update()

    def start_scroll_time(self, x: Coordinate):
        """Start scrolling the time scale."""
        self._time_scale.start_scroll(x)

    def scroll_time_to(self, x: Coordinate):
        """Scroll the time scale to position."""
        self._time_scale.scroll_to(x)
        self.recalculate_all_panes()

    def end_scroll_time(self):
        """End time scale scrolling."""
        self._time_scale.end_scroll()
        self.light_update()

    def zoom_time(self, point_x: Coordinate, scale: float):
        """Zoom the time scale."""
        time_scale = self.time_scale()
        if time_scale.is_empty() or scale == 0:
            return

        time_scale_width = time_scale.width()
        point_x = max(1, min(point_x, time_scale_width))

        time_scale.zoom(point_x, scale)
        self.recalculate_all_panes()

    def start_scale_price(self, pane: Pane, price_scale: PriceScale, x: float):
        """Start scaling a price scale."""
        pane.start_scale_price(price_scale, x)

    def scale_price_to(self, pane: Pane, price_scale: PriceScale, x: float):
        """Scale price scale to position."""
        pane.scale_price_to(price_scale, x)
        self.update_crosshair()
        self._invalidate(self._create_pane_invalidate_mask(pane, 'light'))

    def end_scale_price(self, pane: Pane, price_scale: PriceScale):
        """End price scale scaling."""
        pane.end_scale_price(price_scale)
        self._invalidate(self._create_pane_invalidate_mask(pane, 'light'))

    def start_scroll_price(self, pane: Pane, price_scale: PriceScale, x: float):
        """Start scrolling a price scale."""
        if not price_scale.is_auto_scale():
            pane.start_scroll_price(price_scale, x)

    def scroll_price_to(self, pane: Pane, price_scale: PriceScale, x: float):
        """Scroll price scale to position."""
        if not price_scale.is_auto_scale():
            pane.scroll_price_to(price_scale, x)
            self.update_crosshair()
            self._invalidate(self._create_pane_invalidate_mask(pane, 'light'))

    def end_scroll_price(self, pane: Pane, price_scale: PriceScale):
        """End price scale scrolling."""
        if not price_scale.is_auto_scale():
            pane.end_scroll_price(price_scale)
            self._invalidate(self._create_pane_invalidate_mask(pane, 'light'))

    def reset_price_scale(self, pane: Pane, price_scale: PriceScale):
        """Reset price scale to auto-scale."""
        pane.reset_price_scale(price_scale)
        self._invalidate(self._create_pane_invalidate_mask(pane, 'light'))

    def serieses(self) -> List[Any]:
        """Get all series."""
        return self._series.copy()

    def add_series_to_pane(self, series: Any, pane_index: int):
        """Add a series to a pane."""
        pane = self._get_or_create_pane(pane_index)
        self._add_series_to_pane(series, pane)
        self._series.append(series)
        
        if len(self._series) == 1:
            self.full_update()
        else:
            self.light_update()

    def remove_series(self, series: Any):
        """Remove a series from the chart."""
        if series in self._series:
            self._series.remove(series)
            # Would also remove from appropriate pane
            self.light_update()

    def find_price_scale(self, price_scale_id: str, pane_index: int) -> Optional[PriceScaleOnPane]:
        """Find a price scale by ID and pane index."""
        if pane_index >= len(self._panes):
            return None
            
        pane = self._panes[pane_index]
        price_scale = pane.price_scale_by_id(price_scale_id)
        if price_scale is not None:
            return PriceScaleOnPane(price_scale=price_scale, pane=pane)
        return None

    def apply_price_scale_options(self, price_scale_id: str, options: Any, pane_index: int = 0):
        """Apply options to a price scale."""
        price_scale_on_pane = self.find_price_scale(price_scale_id, pane_index)
        if price_scale_on_pane is not None:
            price_scale_on_pane.price_scale.apply_options(options)
            self._price_scales_options_changed.fire()

    def price_scales_options_changed(self):
        """Get the price scales options changed delegate."""
        return self._price_scales_options_changed

    def pane_for_source(self, source: Any) -> Optional[Pane]:
        """Find the pane containing a data source."""
        for pane in self._panes:
            if source in pane.data_sources():
                return pane
        return None

    def get_pane_index(self, pane: Pane) -> int:
        """Get the index of a pane."""
        return self._panes.index(pane)

    def _get_or_create_pane(self, index: int) -> Pane:
        """Get or create a pane at the specified index."""
        if index < len(self._panes):
            return self._panes[index]
        
        # Create new pane
        pane = Pane(self._time_scale, self)
        self._panes.append(pane)
        return pane

    def _add_series_to_pane(self, series: Any, pane: Pane):
        """Add a series to a pane."""
        # For now, just add to default price scale
        price_scale_id = "right"  # Default
        pane.add_data_source(series, price_scale_id)

    def _invalidate(self, mask: Any):
        """Invalidate the chart with the given mask."""
        if self._invalidate_handler:
            self._invalidate_handler(mask)

    def _create_invalidate_mask(self, level: str) -> Any:
        """Create an invalidation mask."""
        # Simplified - would create proper invalidation mask
        return level

    def _create_pane_invalidate_mask(self, pane: Pane, level: str) -> Any:
        """Create an invalidation mask for a specific pane."""
        # Simplified
        return level