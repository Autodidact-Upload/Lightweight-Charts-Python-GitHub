"""
Lightweight Charts for Python - Data types and structures
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum


class SeriesType(Enum):
    """Supported chart series types"""
    CANDLESTICK = "candlestick"
    LINE = "line"
    AREA = "area"
    HISTOGRAM = "histogram"


class AxisLabelFormat(Enum):
    """Axis label formatting options"""
    AUTO = "auto"
    PRICE = "price"
    VOLUME = "volume"
    PERCENT = "percent"


@dataclass
class LineStyleOptions:
    """Line style configuration"""
    color: str = "#2196F3"
    width: int = 2
    style: str = "solid"  # solid, dotted, dashed


@dataclass
class CandleStickStyleOptions:
    """Candlestick styling options"""
    up_color: str = "#26a69a"
    down_color: str = "#ef5350"
    wick_color: str = "#333333"
    border_up_color: str = "#26a69a"
    border_down_color: str = "#ef5350"
    wick_visible: bool = True
    border_visible: bool = True
    body_width: float = 0.6


@dataclass
class HistogramStyleOptions:
    """Histogram styling options"""
    color: str = "#2196F3"
    bar_width: float = 0.6


@dataclass
class AreaStyleOptions:
    """Area chart styling options"""
    line_color: str = "#2196F3"
    fill_color: str = "#2196F3"
    line_width: int = 2
    fill_alpha: float = 0.3


@dataclass
class ChartOptions:
    """Chart configuration options"""
    width: int = 800
    height: int = 600
    title: str = "Chart"
    background_color: str = "#ffffff"
    text_color: str = "#000000"
    grid_color: str = "#e0e0e0"
    show_grid: bool = True
    show_legend: bool = True
    auto_scale: bool = True


@dataclass
class OHLC:
    """OHLC candle data point"""
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "time": self.time,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume
        }


@dataclass
class DataPoint:
    """Generic data point"""
    time: datetime
    value: float

    def as_dict(self) -> Dict[str, Any]:
        return {"time": self.time, "value": self.value}


@dataclass
class CrosshairOptions:
    """Crosshair configuration"""
    enabled: bool = True
    color: str = "#999999"
    width: int = 1
    label_background_color: str = "#000000"
    label_text_color: str = "#ffffff"


@dataclass
class TooltipOptions:
    """Tooltip configuration"""
    enabled: bool = True
    background_color: str = "#000000"
    text_color: str = "#ffffff"
    border_color: str = "#ffffff"
    padding: int = 8
