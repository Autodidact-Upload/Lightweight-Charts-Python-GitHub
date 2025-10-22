"""
Main Chart class - GPU-accelerated financial charting with Vispy
MULTI-PANE: Uses grid layout with separate views for each pane
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, cast

import numpy as np

from .crosshair import Crosshair, CrosshairOptions, CrosshairVisual, PriceMarker, TimeMarker
from .data_types import (
    AreaStyleOptions,
    CandleStickStyleOptions,
    ChartOptions,
    HistogramStyleOptions,
    LineStyleOptions,
)
from .pane import Pane
from .price_scale_visual import PriceScaleVisual
from .scales import PriceScale, PriceScaleOptions, TimeScale
from .series import AreaSeries, BaseSeries, CandlestickSeries, HistogramSeries, LineSeries
from .utils import hex_to_rgb

logger = logging.getLogger(__name__)

try:
    from vispy import app, scene

    HAS_VISPY = True
except ImportError:
    HAS_VISPY = False


class Chart:
    """Main chart container and renderer with GPU acceleration"""

    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        title: str = "Financial Chart",
        background_color: str = "#ffffff",
        fullscreen: bool = False,
        maximized: bool = False,
    ):
        if not HAS_VISPY:
            raise ImportError("Vispy is required. Install with: pip install vispy")

        self.fullscreen = fullscreen
        self.maximized = maximized

        if fullscreen or maximized:
            try:
                from vispy import app as vispy_app

                vispy_app.use_app()
                canvas_temp = vispy_app.Canvas(show=False)
                screen_size = canvas_temp.size
                canvas_temp.close()
                width = screen_size[0]
                height = screen_size[1]
                if maximized:
                    height = int(height * 0.95)
                logger.info(f"{'Fullscreen' if fullscreen else 'Maximized'} mode: {width}x{height}")
            except Exception as e:
                logger.warning(f"Could not detect screen size: {e}, using defaults")
                width = 1920
                height = 1080 if fullscreen else 1020

        self.width = width
        self.height = height
        self.title = title
        self._bg_color_tuple = hex_to_rgb(background_color)

        self.series: Dict[str, BaseSeries] = {}
        self.time_scale = TimeScale([])
        self.price_scale = PriceScale()

        # Multi-pane support
        self.panes: List[Pane] = []
        self.use_panes = False
        self.grid: Optional[Any] = None

        # Crosshair system
        self.crosshair = Crosshair()
        self.crosshair_visual: Optional[CrosshairVisual] = None
        self.price_markers: List[PriceMarker] = []
        self.time_markers: List[TimeMarker] = []

        # Price scale visual
        self.price_scale_visual: Optional[PriceScaleVisual] = None
        self.price_scale_options = PriceScaleOptions()
        self._price_scale_initialized = False

        # Create Vispy canvas
        self.canvas: Any = scene.SceneCanvas(
            title=title,
            size=(width, height),
            bgcolor=background_color,
            keys="interactive",
            fullscreen=fullscreen,
            show=False,
        )

        # Single view for non-pane mode
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = scene.PanZoomCamera(rect=(0, -1, 1000, 2))  # type: ignore[arg-type]
        self.view.camera.interactive = True
        self.view.camera.aspect = None

        # Crosshair
        self.crosshair_visual = None
        self._crosshair_initialized = False

        # Connect mouse events
        self.canvas.events.mouse_move.connect(self._on_mouse_move)
        self.canvas.events.mouse_press.connect(self._on_mouse_leave)

        # Store last mouse position
        self._last_mouse_pos: Optional[Tuple[float, float]] = None
        self._last_data_pos: Optional[Tuple[float, float]] = None

        # Timer for crosshair updates
        from vispy import app as vispy_app

        self._crosshair_timer = vispy_app.Timer(
            interval=0.016, connect=self._update_crosshair_position, start=True
        )
        logger.debug("Chart: Timer started (60 FPS)")

    @property
    def background_color(self) -> Tuple[float, float, float]:
        return self._bg_color_tuple

    def add_line_series(
        self, name: str = "", style: Optional[LineStyleOptions] = None
    ) -> LineSeries:
        series = LineSeries(name, style)
        series.create_visual(self.view)
        self.series[name or f"line_{len(self.series)}"] = series
        return series

    def add_candlestick_series(
        self, name: str = "", style: Optional[CandleStickStyleOptions] = None
    ) -> CandlestickSeries:
        series = CandlestickSeries(name, style)
        series.create_visual(self.view)
        self.series[name or f"candlestick_{len(self.series)}"] = series
        return series

    def add_area_series(
        self, name: str = "", style: Optional[AreaStyleOptions] = None
    ) -> AreaSeries:
        series = AreaSeries(name, style)
        series.create_visual(self.view)
        self.series[name or f"area_{len(self.series)}"] = series
        return series

    def add_histogram_series(
        self, name: str = "", style: Optional[HistogramStyleOptions] = None
    ) -> HistogramSeries:
        if style is None:
            style = HistogramStyleOptions()
        series = HistogramSeries(name, style)
        series.create_visual(self.view)
        self.series[name or f"histogram_{len(self.series)}"] = series
        return series

    def update_price_scale(self) -> None:
        min_prices = []
        max_prices = []

        for series in self.series.values():
            if series.visible:
                visible = series.get_visible_data(self.time_scale)
                min_p, max_p = series._get_price_range(visible)
                min_prices.append(min_p)
                max_prices.append(max_p)

        if min_prices and max_prices:
            self.price_scale.update_range(min(min_prices), max(max_prices), auto_pad=True)
        else:
            self.price_scale.update_range(0, 100)

    def update_time_scale_data(self, data: List[Any]) -> None:
        self.time_scale.set_data(data)

    def render(self) -> None:
        """Render and display the chart."""

        if self.use_panes and self.panes:
            # MULTI-PANE MODE: Create grid layout with separate views
            logger.info(f"Chart: Multi-pane mode - creating grid with {len(self.panes)} panes")
            self._setup_multi_pane_layout()
        else:
            # SINGLE PANE MODE
            if not self._crosshair_initialized:
                try:
                    self.crosshair_visual = CrosshairVisual(self.view)
                    self._crosshair_initialized = True
                    logger.info("Chart: ✅ Crosshair created")
                except Exception as e:
                    logger.error(f"Chart: ❌ Crosshair failed: {e}")

            if not self._price_scale_initialized and self.price_scale_options.visible:
                try:
                    self.price_scale_visual = PriceScaleVisual(
                        view=self.view,
                        price_scale=self.price_scale,
                        options=self.price_scale_options,
                        position="right",
                    )
                    self._price_scale_initialized = True
                    logger.info("Chart: ✅ Price scale created")
                except Exception as e:
                    logger.error(f"Chart: ❌ Price scale failed: {e}")

            self.update_price_scale()
            for series in self.series.values():
                if series.visible:
                    series.update_visual(self.time_scale, self.price_scale)

            if self.price_scale_visual:
                self.price_scale_visual.update(
                    visible_data_range=self.time_scale.visible_range,
                    canvas_width=self.width,
                    canvas_height=self.height,
                )

        self.canvas.show()

        if self.maximized:
            try:
                self.canvas.native.showMaximized()
            except Exception as e:
                logger.warning(f"Could not maximize: {e}")

        app.run()

    def _setup_multi_pane_layout(self) -> None:
        """Setup grid layout for multi-pane mode with separate views and proper heights."""
        # Clear old view
        self.view.parent = None

        # Create grid with spacing=0 to avoid gaps
        self.grid = self.canvas.central_widget.add_grid(spacing=0)

        # Calculate total ratio
        total_ratio = sum(p.height_ratio for p in self.panes)
        if total_ratio == 0:
            total_ratio = 1.0

        # Mark first pane as main (allows full pan/zoom)
        if self.panes:
            self.panes[0].is_main_pane = True
            logger.info(f"Pane '{self.panes[0].name}' set as MAIN (full pan/zoom)")

        # Create views for each pane
        for i, pane in enumerate(self.panes):
            # Create view in grid
            pane.create_view(self.grid, row=i, col=0)

            # Add separator line at the top of each pane (except the first)
            if i > 0:
                self._add_pane_border(pane)

            # Update pane data
            pane.update_price_scale()
            pane.update_visuals()

        # AFTER creating all views, set row heights using stretch factors
        # This is the correct way to control row heights in Vispy grid
        for i, pane in enumerate(self.panes):
            # Use height_ratio as stretch factor (larger ratio = more space)
            self.grid[i, 0].stretch = (1, pane.height_ratio)  # type: ignore[index]
            logger.info(f"Pane '{pane.name}': row {i}, stretch factor {pane.height_ratio}")

        logger.info(f"✅ Multi-pane grid created: {len(self.panes)} panes!")

    def _add_pane_border(self, pane: Pane) -> None:
        """Add a border line at the top of a pane."""
        if not pane.view:
            return

        try:
            from vispy.scene import visuals

            # Get visible X range
            x_start, x_end = self.time_scale.visible_range

            # Extend line across full width
            x_padding = (x_end - x_start) * 0.05
            x_left = x_start - x_padding
            x_right = x_end + x_padding

            # Draw line at the top of this pane's viewport (y=1.0)
            line = visuals.Line(  # type: ignore[attr-defined]
                pos=np.array([[x_left, 1.0, 0], [x_right, 1.0, 0]]),
                color=(0.3, 0.3, 0.3, 1.0),  # Dark gray, fully opaque
                width=2,  # Slightly thicker for visibility
                connect="strip",
                antialias=True,
            )

            # Add to this pane's view
            pane.view.add(line)
            line.order = 1000  # Render on top of everything

            logger.debug(f"Added border to pane '{pane.name}'")
        except Exception as e:
            logger.error(f"Failed to add pane border: {e}")

    def pan(self, delta: float) -> None:
        self.time_scale.pan(delta)
        self.update_price_scale()
        self._update_visuals()

    def zoom(self, factor: float, center: Optional[float] = None) -> None:
        self.time_scale.zoom(factor, center)
        self.update_price_scale()
        self._update_visuals()

    def _update_visuals(self) -> None:
        for series in self.series.values():
            if series.visible:
                series.update_visual(self.time_scale, self.price_scale)

        if self.price_scale_visual:
            self.price_scale_visual.update(
                visible_data_range=self.time_scale.visible_range,
                canvas_width=self.width,
                canvas_height=self.height,
            )

    def get_series(self, name: str) -> Optional[BaseSeries]:
        return self.series.get(name)

    def remove_series(self, name: str) -> bool:
        if name in self.series:
            series = self.series.pop(name)
            for visual in series.visuals.values():
                try:
                    visual.parent = None
                except Exception:
                    pass
            return True
        return False

    def set_series_visible(self, name: str, visible: bool) -> None:
        if name in self.series:
            self.series[name].visible = visible

    def clear_series(self) -> None:
        for series in list(self.series.values()):
            for visual in series.visuals.values():
                try:
                    visual.parent = None
                except Exception:
                    pass
        self.series.clear()

    def set_background_color(self, color: str) -> None:
        self._bg_color_tuple = hex_to_rgb(color)
        self.canvas.bgcolor = color

    def get_chart_size(self) -> Tuple[int, int]:
        return (self.width, self.height)

    def set_chart_size(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.canvas.size = (width, height)

    def export_image(self, filepath: str) -> None:
        try:
            from vispy.io import write_png

            write_png(filepath, self.canvas.render())
        except ImportError:
            raise ImportError("PIL/Pillow required for image export")

    def subscribe_crosshair_move(self, callback: Any) -> None:
        self.crosshair.on_move(callback)

    def subscribe_crosshair_leave(self, callback: Any) -> None:
        self.crosshair.on_leave(callback)

    def add_price_marker(self, marker: PriceMarker) -> None:
        self.price_markers.append(marker)

    def add_time_marker(self, marker: TimeMarker) -> None:
        self.time_markers.append(marker)

    def clear_markers(self) -> None:
        self.price_markers.clear()
        self.time_markers.clear()

    def get_crosshair_data(self) -> Dict[str, Any]:
        return self.crosshair.get_tooltip_data()

    # ========== Multi-Pane Support ==========

    def add_pane(self, name: str = "", height_ratio: float = 1.0) -> Pane:
        """Add a pane to the chart. Each pane gets its own independent view."""
        self.use_panes = True

        pane_name = name or f"pane_{len(self.panes)}"
        pane = Pane(
            name=pane_name,
            height_ratio=height_ratio,
            parent_view=None,  # Will be set when grid is created
            time_scale=self.time_scale,
        )

        self.panes.append(pane)
        logger.info(f"Added pane: {pane_name} with height_ratio={height_ratio}")

        return pane

    def get_pane(self, name: str) -> Optional[Pane]:
        for pane in self.panes:
            if pane.name == name:
                return pane
        return None

    def remove_pane(self, name: str) -> bool:
        for i, pane in enumerate(self.panes):
            if pane.name == name:
                pane.clear_series()
                self.panes.pop(i)
                logger.info(f"Removed pane: {name}")
                return True
        return False

    def _on_mouse_move(self, event: Any) -> None:
        """Handle mouse move for crosshair updates."""
        if not self.time_scale.data:
            return

        if self.use_panes:
            # Multi-pane mode: update crosshairs in all panes
            for pane in self.panes:
                if not pane.view:
                    continue

                try:
                    # Transform mouse position to this pane's data coordinates
                    tr = pane.view.scene.transform
                    data_pos_result = tr.imap(event.pos[:2])

                    if data_pos_result is None:
                        continue

                    # Type cast for Pylance
                    data_pos = cast(Tuple[float, float], data_pos_result)
                    x_data = data_pos[0]
                    y_data = data_pos[1]

                    start_idx, end_idx = self.time_scale.visible_range

                    # Update crosshair in this pane
                    pane.update_crosshair(x_data, y_data, (start_idx, end_idx))
                except Exception as e:
                    logger.error(f"Error updating crosshair in pane '{pane.name}': {e}")
        else:
            # Single view mode
            if not self.crosshair_visual:
                return

            try:
                pos = event.pos
                self._last_mouse_pos = (pos[0], pos[1])

                tr = self.view.scene.transform
                data_pos_result = tr.imap(pos[:2])

                if data_pos_result is None:
                    return

                # Type cast for Pylance
                data_pos = cast(Tuple[float, float], data_pos_result)
                x_data = data_pos[0]
                y_data = data_pos[1]

                start_idx, end_idx = self.time_scale.visible_range

                self.crosshair_visual.update_position(
                    x=x_data, y=y_data, x_range=(start_idx, end_idx)
                )

                data_index = int(round(x_data))
                is_over_data = (
                    0 <= data_index < len(self.time_scale.data) and start_idx <= x_data <= end_idx
                )

                price_value = self.price_scale.get_price_at_y(y_data)

                if is_over_data:
                    data_point = self.time_scale.data[data_index]
                    time_value = (
                        data_point.get("time")
                        if isinstance(data_point, dict)
                        else getattr(data_point, "time", None)
                    )

                    self.crosshair.set_position(
                        x=x_data,
                        y=y_data,
                        time=time_value,
                        price=price_value,
                        data_index=data_index,
                        series_data=data_point,
                    )
                else:
                    self.crosshair.set_position(
                        x=x_data,
                        y=y_data,
                        time=None,
                        price=price_value,
                        data_index=None,
                        series_data=None,
                    )
            except Exception as e:
                logger.error(f"Chart: Error in mouse move: {e}")

    def _on_mouse_leave(self, event: Any) -> None:
        """Hide crosshairs when mouse leaves."""
        if self.use_panes:
            # Hide crosshairs in all panes
            for pane in self.panes:
                pane.hide_crosshair()
        else:
            # Single view mode
            if self.crosshair_visual:
                self.crosshair_visual.hide()

        self.crosshair.clear_position()
        self._last_mouse_pos = None
        self._last_data_pos = None

    def _update_crosshair_position(self, event: Any = None) -> None:
        if not self.crosshair_visual or not self.time_scale.data:
            return

        if not self.crosshair.visible:
            return

        try:
            mouse_pos = self.canvas.native.mapFromGlobal(self.canvas.native.cursor().pos())
            canvas_pos = (mouse_pos.x(), mouse_pos.y())

            tr = self.view.scene.transform
            data_pos_result = tr.imap(canvas_pos)

            if data_pos_result is None:
                return

            # Type cast for Pylance
            data_pos = cast(Tuple[float, float], data_pos_result)
            x_data = data_pos[0]
            y_data = data_pos[1]

            start_idx, end_idx = self.time_scale.visible_range

            self.crosshair_visual.update_position(x=x_data, y=y_data, x_range=(start_idx, end_idx))
        except Exception:
            pass

    def enable_crosshair(self, enabled: bool = True) -> None:
        if self.crosshair_visual:
            self.crosshair_visual.set_visible(enabled)

    def set_crosshair_colors(
        self, vert_color: str = "#999999", horiz_color: str = "#999999"
    ) -> None:
        """Set crosshair colors for all panes."""
        if self.use_panes:
            # Set colors for all panes
            for pane in self.panes:
                pane.set_crosshair_colors(vert_color, horiz_color)
        else:
            # Single view mode
            if self.crosshair_visual:
                self.crosshair_visual.update_colors(vert_color, horiz_color)

    def configure_price_scale(self, options: PriceScaleOptions) -> None:
        self.price_scale_options = options
        if self.price_scale_visual:
            self.price_scale_visual.options = options
            self.price_scale_visual.update(
                visible_data_range=self.time_scale.visible_range,
                canvas_width=self.width,
                canvas_height=self.height,
                force=True,
            )

    def show_price_scale(self, visible: bool = True) -> None:
        if self.price_scale_visual:
            if visible:
                self.price_scale_visual.show()
            else:
                self.price_scale_visual.hide()
