"""
Pane system for multi-pane charts
Allows separate panes for price action, indicators, etc.
"""

from typing import Dict, Optional, List, Any
import logging
from .series import BaseSeries, LineSeries, CandlestickSeries, AreaSeries, HistogramSeries
from .scales import TimeScale, PriceScale
from .data_types import (
    LineStyleOptions,
    CandleStickStyleOptions,
    AreaStyleOptions,
    HistogramStyleOptions
)

logger = logging.getLogger(__name__)

try:
    from vispy import scene
    HAS_VISPY = True
except ImportError:
    HAS_VISPY = False


class Pane:
    """
    A single pane in a multi-pane chart.
    Each pane has its own price scale, view, and camera for independent scrolling.
    """
    
    def __init__(
        self,
        name: str,
        height_ratio: float = 1.0,
        parent_view: Any = None,
        time_scale: Optional[TimeScale] = None
    ):
        """
        Initialize Pane.
        
        Args:
            name: Pane identifier
            height_ratio: Height as ratio of total (0.0 to 1.0)
            parent_view: Parent Vispy view grid
            time_scale: Shared time scale across all panes
        """
        self.name = name
        self.height_ratio = height_ratio
        self.parent_view = parent_view
        self.time_scale = time_scale or TimeScale([])
        self.price_scale = PriceScale()
        
        # Series in this pane
        self.series: Dict[str, BaseSeries] = {}
        
        # Vispy view for this pane (created later)
        self.view: Optional[Any] = None
        
        # Crosshair visual for this pane
        self.crosshair_visual: Optional[Any] = None
        
        # Position in layout
        self.y_position = 0.0
        self._y_min = -1.0
        self._y_max = 1.0
        
        # Track if this is the main pane
        self.is_main_pane = False
        
        logger.debug(f"Pane created: {name} (height_ratio={height_ratio})")
    
    def create_view(self, grid: Any, row: int, col: int = 0) -> None:
        """
        Create Vispy view for this pane in a grid layout.
        
        Args:
            grid: Parent ViewBox grid
            row: Row index in grid
            col: Column index in grid
        """
        if not HAS_VISPY:
            logger.warning("Vispy not available")
            return
        
        try:
            # Add view to grid at specified row
            self.view = grid.add_view(row=row, col=col)
            
            # Create camera for this view
            visible_start, visible_end = self.time_scale.visible_range
            camera = scene.PanZoomCamera(  # type: ignore[attr-defined,arg-type]
                rect=(visible_start, -1, visible_end - visible_start, 2)  # type: ignore[arg-type]
            )
            self.view.camera = camera  # type: ignore[attr-defined]
            camera.aspect = None
            
            # Main pane: full interactivity
            # Other panes: horizontal scroll only (Y locked)
            if self.is_main_pane:
                camera.interactive = True
                logger.info(f"Pane '{self.name}': MAIN pane with full pan/zoom")
            else:
                # Lock Y-axis for non-main panes
                self._setup_locked_camera()
                logger.info(f"Pane '{self.name}': Y-axis LOCKED (horizontal only)")
            
            # Create crosshair for this pane
            self._create_crosshair()
            
            # NOW create visuals for all series that were added before view was ready
            for series in self.series.values():
                series.create_visual(self.view)
                logger.debug(f"Pane '{self.name}': Created visual for series '{series.name}'")
            
            logger.info(f"✅ Pane view created: {self.name} at grid row {row}")
        except Exception as e:
            logger.error(f"Failed to create pane view: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_crosshair(self) -> None:
        """Create crosshair visual for this pane."""
        if not self.view:
            return
        
        try:
            from .crosshair import CrosshairVisual
            self.crosshair_visual = CrosshairVisual(self.view)
            logger.debug(f"Pane '{self.name}': Crosshair created")
        except Exception as e:
            logger.error(f"Pane '{self.name}': Failed to create crosshair: {e}")
    
    def update_crosshair(self, x: float, y: float, x_range: tuple) -> None:
        """Update crosshair position in this pane."""
        if self.crosshair_visual:
            self.crosshair_visual.update_position(x, y, x_range)
    
    def hide_crosshair(self) -> None:
        """Hide crosshair in this pane."""
        if self.crosshair_visual:
            self.crosshair_visual.hide()
    
    def set_crosshair_colors(self, vert_color: str, horiz_color: str) -> None:
        """Set crosshair colors for this pane."""
        if self.crosshair_visual:
            self.crosshair_visual.update_colors(vert_color, horiz_color)
    
    def _setup_locked_camera(self) -> None:
        """Setup camera to only allow horizontal (X-axis) pan/zoom."""
        if not self.view or not self.view.camera:
            return
        
        pane_ref = self
        
        def locked_mouse_handler(event):
            """Only allow horizontal pan/zoom - Y is LOCKED!"""
            if event.handled or not pane_ref.view or not pane_ref.view.camera:
                return
            
            if event.type == 'mouse_wheel':
                # Zoom horizontally only
                s = 1.1 ** (event.delta[1] * 30)
                pane_ref.view.camera.zoom((s, 1.0), center=event.pos[:2])
                event.handled = True
                
            elif event.type == 'mouse_move' and event.is_dragging and event.button == 1:
                # Pan horizontally only
                p1 = event.last_event.pos[:2]
                p2 = event.pos[:2]
                p1_scene = pane_ref.view.camera.transform.imap(p1)
                p2_scene = pane_ref.view.camera.transform.imap(p2)
                
                if p1_scene is not None and p2_scene is not None:
                    dx = p2_scene[0] - p1_scene[0]
                    rect = pane_ref.view.camera.rect
                    # Pan X only, keep Y fixed!
                    pane_ref.view.camera.rect = (rect[0] - dx, rect[1], rect[2], rect[3])
                    event.handled = True
        
        self.view.camera.viewbox_mouse_event = locked_mouse_handler  # type: ignore[attr-defined]
        self.view.camera.interactive = True
    
    def add_line_series(
        self,
        name: str = "",
        style: Optional[LineStyleOptions] = None
    ) -> LineSeries:
        """Add a line series to this pane."""
        series = LineSeries(name, style)
        # Only create visual if view exists, otherwise defer until create_view()
        if self.view:
            series.create_visual(self.view)
        self.series[name or f"line_{len(self.series)}"] = series
        logger.debug(f"Pane {self.name}: Added line series '{name}'")
        return series
    
    def add_candlestick_series(
        self,
        name: str = "",
        style: Optional[CandleStickStyleOptions] = None
    ) -> CandlestickSeries:
        """Add a candlestick series to this pane."""
        series = CandlestickSeries(name, style)
        # Only create visual if view exists
        if self.view:
            series.create_visual(self.view)
        self.series[name or f"candlestick_{len(self.series)}"] = series
        logger.debug(f"Pane {self.name}: Added candlestick series '{name}'")
        return series
    
    def add_area_series(
        self,
        name: str = "",
        style: Optional[AreaStyleOptions] = None
    ) -> AreaSeries:
        """Add an area series to this pane."""
        series = AreaSeries(name, style)
        # Only create visual if view exists
        if self.view:
            series.create_visual(self.view)
        self.series[name or f"area_{len(self.series)}"] = series
        logger.debug(f"Pane {self.name}: Added area series '{name}'")
        return series
    
    def add_histogram_series(
        self,
        name: str = "",
        style: Optional[HistogramStyleOptions] = None
    ) -> HistogramSeries:
        """Add a histogram series to this pane."""
        if style is None:
            style = HistogramStyleOptions()
        series = HistogramSeries(name, style)
        # Only create visual if view exists
        if self.view:
            series.create_visual(self.view)
        self.series[name or f"histogram_{len(self.series)}"] = series
        logger.debug(f"Pane {self.name}: Added histogram series '{name}'")
        return series
    
    def update_price_scale(self) -> None:
        """Update price scale based on visible data in this pane."""
        min_prices = []
        max_prices = []
        
        for series in self.series.values():
            if series.visible:
                visible = series.get_visible_data(self.time_scale)
                if visible:
                    min_p, max_p = series._get_price_range(visible)
                    min_prices.append(min_p)
                    max_prices.append(max_p)
        
        if min_prices and max_prices:
            self.price_scale.update_range(
                min(min_prices),
                max(max_prices),
                auto_pad=True
            )
            logger.debug(f"Pane {self.name}: Price scale {min(min_prices):.2f} - {max(max_prices):.2f}")
        else:
            self.price_scale.update_range(0, 100)
    
    def update_visuals(self) -> None:
        """Update all series visuals in this pane."""
        for series in self.series.values():
            if series.visible:
                try:
                    series.update_visual(self.time_scale, self.price_scale)
                except Exception as e:
                    logger.error(f"Pane {self.name}: Failed to update series '{series.name}': {e}")
    
    def sync_horizontal_view(self, x: float, width: float) -> None:
        """
        Synchronize horizontal (X-axis) view with other panes.
        
        Args:
            x: X position (time index)
            width: Width of view
        """
        if self.view and self.view.camera:
            rect = self.view.camera.rect
            # Update X and width, keep Y and height the same
            self.view.camera.rect = (x, rect[1], width, rect[3])
    
    def get_series(self, name: str) -> Optional[BaseSeries]:
        """Get series by name from this pane."""
        return self.series.get(name)
    
    def remove_series(self, name: str) -> bool:
        """Remove series from this pane."""
        if name in self.series:
            series = self.series.pop(name)
            for visual in series.visuals.values():
                try:
                    visual.parent = None
                except Exception:
                    pass
            logger.debug(f"Pane {self.name}: Removed series '{name}'")
            return True
        return False
    
    def clear_series(self) -> None:
        """Clear all series from this pane."""
        for series in list(self.series.values()):
            for visual in series.visuals.values():
                try:
                    visual.parent = None
                except Exception:
                    pass
        self.series.clear()
        logger.debug(f"Pane {self.name}: Cleared all series")
