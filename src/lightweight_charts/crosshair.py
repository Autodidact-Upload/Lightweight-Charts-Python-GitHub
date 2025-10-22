"""
Crosshair system - OPTIMIZED with far fewer segments
"""

import logging

try:
    from vispy.scene import visuals  # type: ignore[import]
    import numpy as np
    HAS_VISPY = True
except ImportError:
    HAS_VISPY = False

logger = logging.getLogger(__name__)

from typing import Optional, Tuple, Callable, Dict, Any, List
from datetime import datetime
from .utils import format_price


class CrosshairOptions:
    """Configuration for crosshair display"""
    
    def __init__(
        self,
        mode: str = "normal",
        vert_color: str = "#999999",
        horiz_color: str = "#999999",
        vert_style: str = "dashed",
        horiz_style: str = "dashed",
        width: int = 1,
        dash_length: float = 10.0,
        gap_length: float = 5.0,
        label_background: str = "#131722",
        label_text_color: str = "#FFFFFF",
        visible: bool = True
    ):
        self.mode = mode
        self.vert_color = vert_color
        self.horiz_color = horiz_color
        self.vert_style = vert_style
        self.horiz_style = horiz_style
        self.width = width
        self.dash_length = dash_length
        self.gap_length = gap_length
        self.label_background = label_background
        self.label_text_color = label_text_color
        self.visible = visible


class CrosshairPosition:
    """Current crosshair position and data"""
    
    def __init__(
        self,
        x: float,
        y: float,
        time: Optional[datetime] = None,
        price: Optional[float] = None,
        data_index: Optional[int] = None,
        series_data: Optional[Dict[str, Any]] = None
    ):
        self.x = x
        self.y = y
        self.time = time
        self.price = price
        self.data_index = data_index
        self.series_data = series_data or {}


class Crosshair:
    """Crosshair implementation for interactive chart navigation."""
    
    def __init__(self, options: Optional[CrosshairOptions] = None):
        self.options = options or CrosshairOptions()
        self.position: Optional[CrosshairPosition] = None
        self.visible = False
        self._move_callbacks: List[Callable] = []
        self._leave_callbacks: List[Callable] = []
    
    def set_position(
        self, x: float, y: float, time: Optional[datetime] = None,
        price: Optional[float] = None, data_index: Optional[int] = None,
        series_data: Optional[Dict[str, Any]] = None
    ) -> None:
        self.visible = True
        self.position = CrosshairPosition(x, y, time, price, data_index, series_data)
        for callback in self._move_callbacks:
            callback(self.position)
    
    def clear_position(self) -> None:
        self.visible = False
        self.position = None
        for callback in self._leave_callbacks:
            callback()
    
    def on_move(self, callback: Callable) -> None:
        self._move_callbacks.append(callback)
    
    def on_leave(self, callback: Callable) -> None:
        self._leave_callbacks.append(callback)
    
    def get_price_label(self) -> str:
        if not self.position or self.position.price is None:
            return ""
        return format_price(self.position.price)
    
    def get_time_label(self) -> str:
        if not self.position or not self.position.time:
            return ""
        return self.position.time.strftime("%Y-%m-%d %H:%M")
    
    def get_tooltip_data(self) -> Dict[str, Any]:
        if not self.position or not self.position.series_data:
            return {}
        data = self.position.series_data
        tooltip = {"time": self.get_time_label(), "price": self.get_price_label()}
        if "open" in data:
            tooltip.update({
                "open": format_price(data["open"]),
                "high": format_price(data["high"]),
                "low": format_price(data["low"]),
                "close": format_price(data["close"])
            })
        if "volume" in data:
            tooltip["volume"] = f"{data['volume']:,.0f}"
        if "value" in data:
            tooltip["value"] = format_price(data["value"])
        return tooltip
    
    def show(self) -> None:
        self.visible = True
    
    def hide(self) -> None:
        self.visible = False
    
    def toggle(self) -> None:
        self.visible = not self.visible


class PriceMarker:
    def __init__(self, price: float, color: str = "#2196F3", 
                 text_color: str = "#FFFFFF", label: Optional[str] = None):
        self.price = price
        self.color = color
        self.text_color = text_color
        self.label = label or format_price(price)


class TimeMarker:
    def __init__(self, time: datetime, color: str = "#2196F3",
                 text_color: str = "#FFFFFF", label: Optional[str] = None):
        self.time = time
        self.color = color
        self.text_color = text_color
        self.label = label or time.strftime("%Y-%m-%d")


class CrosshairVisual:
    """OPTIMIZED: Use SOLID lines - dashed is too laggy!"""
    
    def __init__(self, view, options: Optional[CrosshairOptions] = None):
        if not HAS_VISPY:
            logger.warning("Vispy not available")
            return
        
        self.view = view
        self.options = options or CrosshairOptions()
        self._initialized = False
        
        from .utils import hex_to_rgba
        
        # SOLID LINES - much faster!
        v_color = hex_to_rgba(self.options.vert_color, 0.6)  # Semi-transparent
        self.v_line = visuals.Line(  # type: ignore[attr-defined]
            pos=np.array([[0, -100000, 0], [0, 100000, 0]], dtype=np.float32),
            color=v_color,
            width=1,
            connect='strip',  # Solid line
            method='gl',
            antialias=True
        )
        
        h_color = hex_to_rgba(self.options.horiz_color, 0.6)  # Semi-transparent
        self.h_line = visuals.Line(  # type: ignore[attr-defined]
            pos=np.array([[-100000, 0, 0], [100000, 0, 0]], dtype=np.float32),
            color=h_color,
            width=1,
            connect='strip',  # Solid line
            method='gl',
            antialias=True
        )
        
        try:
            view.add(self.v_line)
            view.add(self.h_line)
            
            self.v_line.order = 10000
            self.h_line.order = 10000
            
            self.v_line.set_gl_state('translucent', depth_test=False, cull_face=False)
            self.h_line.set_gl_state('translucent', depth_test=False, cull_face=False)
            
            self.v_line.visible = True
            self.h_line.visible = True
            
            self._initialized = True
            
            logger.info("CrosshairVisual: ✅ Created SOLID crosshair lines (optimized)")
        except Exception as e:
            logger.error(f"CrosshairVisual: ❌ Failed: {e}")
            import traceback
            traceback.print_exc()
    
    def update_position(self, x: float, y: float, x_range: Tuple[float, float]) -> None:
        """Update with simple solid lines - NO lag!"""
        if not self._initialized:
            return
        
        try:
            # Vertical line: fixed X, full Y range
            v_pos = np.array([[x, -100000, 0], [x, 100000, 0]], dtype=np.float32)
            self.v_line.set_data(v_pos)
            
            # Horizontal line: fixed Y, full X range
            h_pos = np.array([[-100000, y, 0], [100000, y, 0]], dtype=np.float32)
            self.h_line.set_data(h_pos)
            
            if not self.v_line.visible:
                self.show()
                
        except Exception as e:
            pass  # Silent
    
    def show(self) -> None:
        if not self._initialized:
            return
        if HAS_VISPY and self.options.visible:
            try:
                self.v_line.visible = True
                self.h_line.visible = True
            except:
                pass
    
    def hide(self) -> None:
        if not self._initialized:
            return
        if HAS_VISPY:
            try:
                self.v_line.visible = False
                self.h_line.visible = False
            except:
                pass
    
    def set_visible(self, visible: bool) -> None:
        self.options.visible = visible
        if visible:
            self.show()
        else:
            self.hide()
    
    def update_colors(self, vert_color: str, horiz_color: str) -> None:
        if not self._initialized:
            return
        from .utils import hex_to_rgba
        try:
            self.v_line.color = hex_to_rgba(vert_color, 0.6)
            self.h_line.color = hex_to_rgba(horiz_color, 0.6)
            self.options.vert_color = vert_color
            self.options.horiz_color = horiz_color
        except:
            pass
