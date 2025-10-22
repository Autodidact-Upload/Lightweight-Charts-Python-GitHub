"""
Visual price scale rendering with Vispy
Displays price labels, tick marks, and border on chart edge
"""

import logging
import numpy as np
from typing import List, Tuple, Optional, Any

logger = logging.getLogger(__name__)

try:
    from vispy.scene import visuals  # type: ignore[import]
    from vispy import app
    HAS_VISPY = True
except ImportError:
    HAS_VISPY = False
    visuals = None  # type: ignore[assignment]

from .scales import PriceScale, PriceScaleOptions, PriceScaleMode, PriceScaleMargins
from .utils import hex_to_rgb, hex_to_rgba


class PriceScaleVisual:
    """
    Renders the visual price scale on the right (or left) side of the chart.
    
    Components:
    - Price labels (text)
    - Tick marks (horizontal lines)
    - Border line
    - Background (optional)
    """
    
    def __init__(
        self,
        view: Any,
        price_scale: PriceScale,
        options: Optional[PriceScaleOptions] = None,
        position: str = "right"
    ):
        """
        Initialize PriceScaleVisual.
        
        Args:
            view: Vispy view to attach visuals to
            price_scale: PriceScale data model
            options: Visual options
            position: "right" or "left" (default: "right")
        """
        if not HAS_VISPY:
            logger.error("Vispy not available - price scale cannot be rendered")
            return
        
        self.view = view
        self.price_scale = price_scale
        self.options = options or PriceScaleOptions()
        self.position = position
        
        # Calculate scale width (pixels)
        self.width = max(self.options.minimum_width, 60)
        
        # Visual components
        self.border_line = None
        self.tick_visuals: List[Any] = []
        self.label_visuals: List[Any] = []
        
        # Track last rendered state to avoid unnecessary updates
        self._last_min_value = None
        self._last_max_value = None
        self._last_num_labels = 0
        
        # Create initial visuals
        self._create_visuals()
        
        logger.info(f"PriceScaleVisual created at position: {position}")
    
    def _create_visuals(self) -> None:
        """Create initial Vispy visual components."""
        if not self.options.visible or not HAS_VISPY:
            return
        
        # Create border line
        if self.options.border_visible:
            self._create_border()
        
        logger.debug("Price scale visuals created")
    
    def _create_border(self) -> None:
        """Create border line between scale and chart."""
        if not HAS_VISPY or visuals is None:
            return
        
        try:
            border_color = hex_to_rgba(self.options.border_color, 1.0)
            
            # Vertical line - will be positioned during update
            self.border_line = visuals.Line(  # type: ignore[attr-defined]
                pos=np.array([[0, -100000, 0], [0, 100000, 0]], dtype=np.float32),
                color=border_color,
                width=1,
                connect='strip',
                method='gl',
                antialias=True
            )
            self.view.add(self.border_line)
            self.border_line.order = 100  # Render on top of data
            
            logger.debug("Price scale border created")
        except Exception as e:
            logger.error(f"Failed to create border: {e}")
    
    def update(
        self,
        visible_data_range: Tuple[float, float],
        canvas_width: int,
        canvas_height: int,
        force: bool = False
    ) -> None:
        """
        Update price scale visuals based on current chart state.
        
        Args:
            visible_data_range: (x_start, x_end) visible range in data coordinates
            canvas_width: Canvas width in pixels
            canvas_height: Canvas height in pixels
            force: Force update even if values haven't changed
        """
        if not self.options.visible or not HAS_VISPY:
            return
        
        # Always update border position (stays at window edge during pan/zoom)
        self._update_border_position(visible_data_range, canvas_width)
        
        # Check if we need to regenerate labels
        need_regenerate = force or (
            self._last_min_value != self.price_scale.min_value or
            self._last_max_value != self.price_scale.max_value
        )
        
        if need_regenerate:
            # Update cached values
            self._last_min_value = self.price_scale.min_value
            self._last_max_value = self.price_scale.max_value
            
            # Generate price labels
            price_labels = self._generate_price_labels()
            
            # Recreate price labels and ticks
            self._update_labels_and_ticks(price_labels, visible_data_range, canvas_width)
            
            logger.debug(f"Price scale updated with {len(price_labels)} labels")
        else:
            # Just update positions (for pan/zoom without price change)
            self._update_label_positions(canvas_width)
    
    def _generate_price_labels(self, num_labels: int = 8) -> List[Tuple[float, str]]:
        """
        Generate price labels for current visible range.
        
        Args:
            num_labels: Number of labels to generate
        
        Returns:
            List of (price_value, label_text) tuples
        """
        if self.options.mode == PriceScaleMode.LOGARITHMIC:
            return self._generate_logarithmic_labels(num_labels)
        elif self.options.mode == PriceScaleMode.PERCENTAGE:
            return self._generate_percentage_labels(num_labels)
        elif self.options.mode == PriceScaleMode.INDEXED_TO_100:
            return self._generate_indexed_labels(num_labels)
        else:
            # Normal mode
            return self.price_scale.get_labels(num_labels)
    
    def _generate_logarithmic_labels(self, num_labels: int) -> List[Tuple[float, str]]:
        """Generate labels for logarithmic scale."""
        min_val = self.price_scale.min_value
        max_val = self.price_scale.max_value
        
        if min_val <= 0:
            min_val = 0.01  # Avoid log(0)
        
        log_min = np.log10(min_val)
        log_max = np.log10(max_val)
        
        log_values = np.linspace(log_min, log_max, num_labels)
        values = 10 ** log_values
        
        return [(v, self.price_scale._format_price(v)) for v in values]
    
    def _generate_percentage_labels(self, num_labels: int) -> List[Tuple[float, str]]:
        """Generate labels for percentage mode."""
        values = np.linspace(
            self.price_scale.min_value,
            self.price_scale.max_value,
            num_labels
        )
        return [(v, f"{v:.1f}%") for v in values]
    
    def _generate_indexed_labels(self, num_labels: int) -> List[Tuple[float, str]]:
        """Generate labels for indexed to 100 mode."""
        values = np.linspace(
            self.price_scale.min_value,
            self.price_scale.max_value,
            num_labels
        )
        return [(v, f"{v:.1f}") for v in values]
    
    def _update_border_position(self, visible_data_range: Tuple[float, float], canvas_width: int) -> None:
        """Update border line position at window edge."""
        if not self.border_line:
            return
        
        try:
            # Get the camera's view rectangle
            camera = self.view.camera
            rect = camera.rect
            
            # Position at the right edge of the visible view
            if self.position == "right":
                # Use the right edge of the camera view
                x = rect.left + rect.width
            else:
                # Use the left edge
                x = rect.left
            
            # Update line position (full vertical extent)
            pos = np.array([
                [x, -100000, 0],
                [x, 100000, 0]
            ], dtype=np.float32)
            
            self.border_line.set_data(pos)
        except Exception as e:
            logger.error(f"Failed to update border position: {e}")
    
    def _update_labels_and_ticks(
        self,
        price_labels: List[Tuple[float, str]],
        visible_data_range: Tuple[float, float],
        canvas_width: int
    ) -> None:
        """
        Update price labels and tick marks.
        
        Args:
            price_labels: List of (price, label_text) tuples
            visible_data_range: (x_start, x_end) in data coordinates
            canvas_width: Canvas width in pixels
        """
        if not HAS_VISPY or visuals is None:
            return
        
        # Clear existing labels and ticks
        for label in self.label_visuals:
            try:
                label.parent = None
            except:
                pass
        self.label_visuals.clear()
        
        for tick in self.tick_visuals:
            try:
                tick.parent = None
            except:
                pass
        self.tick_visuals.clear()
        
        # Get camera rect for positioning
        camera = self.view.camera
        rect = camera.rect
        
        # Calculate X position for labels at window edge
        if self.position == "right":
            # Position labels at right edge of view
            label_x = rect.left + rect.width + 0.5  # Slightly beyond border
            tick_x_start = rect.left + rect.width
            tick_x_end = rect.left + rect.width + 0.3
            anchor_x = 'left'
        else:
            # Position labels at left edge of view
            label_x = rect.left - 0.5  # Slightly before border
            tick_x_start = rect.left
            tick_x_end = rect.left - 0.3
            anchor_x = 'right'
        
        # Create new labels and ticks
        text_color = hex_to_rgba(self.options.text_color, 1.0)
        
        for price_value, label_text in price_labels:
            try:
                # Calculate Y position in normalized coordinates
                y_coord = self.price_scale.get_y_at_price(price_value)
                
                # Create text label
                label = visuals.Text(  # type: ignore[attr-defined]
                    text=label_text,
                    pos=(label_x, y_coord, 0),
                    color=text_color,
                    font_size=10,
                    anchor_x=anchor_x,
                    anchor_y='center',
                    method='gpu'
                )
                
                self.view.add(label)
                label.order = 200  # Render on top
                self.label_visuals.append(label)
                
                # Create tick mark if enabled
                if self.options.ticks_visible:
                    self._create_tick_mark(y_coord, tick_x_start, tick_x_end)
                
            except Exception as e:
                logger.error(f"Failed to create label '{label_text}': {e}")
    
    def _update_label_positions(self, canvas_width: int) -> None:
        """
        Update label positions without recreating them.
        Used when camera moves but price range hasn't changed.
        
        Args:
            canvas_width: Canvas width in pixels
        """
        if not self.label_visuals:
            return
        
        try:
            # Get camera rect for positioning
            camera = self.view.camera
            rect = camera.rect
            
            # Calculate new X position
            if self.position == "right":
                label_x = rect.left + rect.width + 0.5
                tick_x_start = rect.left + rect.width
                tick_x_end = rect.left + rect.width + 0.3
            else:
                label_x = rect.left - 0.5
                tick_x_start = rect.left
                tick_x_end = rect.left - 0.3
            
            # Update each label's position
            for label in self.label_visuals:
                old_pos = label.pos
                label.pos = (label_x, old_pos[0][1], 0)
            
            # Update tick mark positions
            if self.options.ticks_visible and self.tick_visuals:
                for tick in self.tick_visuals:
                    old_pos = tick.pos
                    y_coord = old_pos[0][1]
                    tick.set_data(np.array([
                        [tick_x_start, y_coord, 0],
                        [tick_x_end, y_coord, 0]
                    ], dtype=np.float32))
        except Exception as e:
            logger.error(f"Failed to update label positions: {e}")
    
    def _create_tick_mark(
        self,
        y_coord: float,
        x_start: float,
        x_end: float
    ) -> None:
        """
        Create a small horizontal tick mark at the given Y coordinate.
        
        Args:
            y_coord: Y coordinate in normalized space
            x_start: Tick start X coordinate
            x_end: Tick end X coordinate
        """
        if not HAS_VISPY or visuals is None:
            return
        
        try:
            tick_color = hex_to_rgba(self.options.border_color, 0.5)
            
            # Horizontal line
            tick = visuals.Line(  # type: ignore[attr-defined]
                pos=np.array([
                    [x_start, y_coord, 0],
                    [x_end, y_coord, 0]
                ], dtype=np.float32),
                color=tick_color,
                width=1,
                connect='strip',
                method='gl',
                antialias=True
            )
            
            self.view.add(tick)
            tick.order = 150
            self.tick_visuals.append(tick)
            
        except Exception as e:
            logger.error(f"Failed to create tick mark: {e}")
    
    def show(self) -> None:
        """Show the price scale."""
        self.options.visible = True
        if self.border_line:
            self.border_line.visible = True
        for label in self.label_visuals:
            label.visible = True
        for tick in self.tick_visuals:
            tick.visible = True
        logger.debug("Price scale shown")
    
    def hide(self) -> None:
        """Hide the price scale."""
        self.options.visible = False
        if self.border_line:
            self.border_line.visible = False
        for label in self.label_visuals:
            label.visible = False
        for tick in self.tick_visuals:
            tick.visible = False
        logger.debug("Price scale hidden")
    
    def set_width(self, width: int) -> None:
        """
        Set the width of the price scale.
        
        Args:
            width: Width in pixels
        """
        self.width = max(width, self.options.minimum_width)
        logger.debug(f"Price scale width set to: {self.width}px")
    
    def cleanup(self) -> None:
        """Clean up all visuals."""
        # Remove border
        if self.border_line:
            try:
                self.border_line.parent = None
            except:
                pass
            self.border_line = None
        
        # Remove labels
        for label in self.label_visuals:
            try:
                label.parent = None
            except:
                pass
        self.label_visuals.clear()
        
        # Remove ticks
        for tick in self.tick_visuals:
            try:
                tick.parent = None
            except:
                pass
        self.tick_visuals.clear()
        
        logger.debug("Price scale visuals cleaned up")
