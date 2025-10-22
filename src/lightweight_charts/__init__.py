"""
Lightweight Charts for Python - Main package
"""

from .chart import Chart
from .pane import Pane
from .series import (
    BaseSeries,
    LineSeries,
    CandlestickSeries,
    AreaSeries,
    HistogramSeries
)
from .scales import (
    TimeScale,
    PriceScale,
    PriceScaleMode,
    PriceScaleMargins,
    PriceScaleOptions
)
from .data_types import (
    SeriesType,
    AxisLabelFormat,
    LineStyleOptions,
    CandleStickStyleOptions,
    HistogramStyleOptions,
    AreaStyleOptions,
    ChartOptions,
    OHLC,
    DataPoint,
    TooltipOptions
)
from .crosshair import (
    Crosshair,
    CrosshairOptions,
    CrosshairVisual,
    CrosshairPosition,
    PriceMarker,
    TimeMarker
)
from .price_scale_visual import PriceScaleVisual
from .utils import (
    hex_to_rgb,
    hex_to_rgba,
    format_price,
    format_volume,
    normalize_value,
    denormalize_value,
    clamp
)
from .indicators import (
    MovingAverage,
    RSI,
    MACD,
    BollingerBands,
    IndicatorCalculator
)

__version__ = "1.0.0"
__author__ = "TradingView Lightweight Charts Python Port"
__all__ = [
    "Chart",
    "Pane",
    "BaseSeries",
    "LineSeries",
    "CandlestickSeries",
    "AreaSeries",
    "HistogramSeries",
    "TimeScale",
    "PriceScale",
    "PriceScaleMode",
    "PriceScaleMargins",
    "PriceScaleOptions",
    "SeriesType",
    "AxisLabelFormat",
    "LineStyleOptions",
    "CandleStickStyleOptions",
    "HistogramStyleOptions",
    "AreaStyleOptions",
    "ChartOptions",
    "OHLC",
    "DataPoint",
    "TooltipOptions",
    "Crosshair",
    "CrosshairOptions",
    "CrosshairVisual",
    "CrosshairPosition",
    "PriceMarker",
    "TimeMarker",
    "PriceScaleVisual",
    "hex_to_rgb",
    "hex_to_rgba",
    "format_price",
    "format_volume",
    "normalize_value",
    "denormalize_value",
    "clamp",
    "MovingAverage",
    "RSI",
    "MACD",
    "BollingerBands",
    "IndicatorCalculator"
]
