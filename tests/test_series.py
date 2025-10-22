"""
Unit tests for Series classes
"""

import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lightweight_charts import (
    LineSeries,
    CandlestickSeries,
    AreaSeries,
    HistogramSeries,
    LineStyleOptions,
    CandleStickStyleOptions
)


class TestLineSeries:
    """Test LineSeries class"""
    
    def test_initialization(self):
        """Test line series initialization"""
        series = LineSeries("Test Line")
        
        assert series.name == "Test Line"
        assert series.visible == True
        assert len(series.data) == 0
    
    def test_set_data(self):
        """Test setting line data"""
        series = LineSeries()
        data = [
            {"time": datetime(2024, 1, 1), "value": 100},
            {"time": datetime(2024, 1, 2), "value": 102},
        ]
        
        series.set_data(data)
        assert len(series.data) == 2
        assert series.data[0]["value"] == 100
    
    def test_with_custom_style(self):
        """Test line series with custom styling"""
        style = LineStyleOptions(
            color="#FF5722",
            width=3
        )
        series = LineSeries("Styled", style)
        
        assert series.style.color == "#FF5722"
        assert series.style.width == 3


class TestCandlestickSeries:
    """Test CandlestickSeries class"""
    
    def test_initialization(self):
        """Test candlestick series initialization"""
        series = CandlestickSeries("OHLC")
        
        assert series.name == "OHLC"
        assert series.visible == True
    
    def test_set_ohlc_data(self):
        """Test setting OHLC data"""
        series = CandlestickSeries()
        data = [
            {
                "time": datetime(2024, 1, 1),
                "open": 100,
                "high": 102,
                "low": 99,
                "close": 101
            }
        ]
        
        series.set_data(data)
        assert len(series.data) == 1
        assert series.data[0]["close"] == 101
    
    def test_custom_style(self):
        """Test candlestick with custom styling"""
        style = CandleStickStyleOptions(
            up_color="#00FF41",
            down_color="#FF0040"
        )
        series = CandlestickSeries("Styled", style)
        
        assert series.style.up_color == "#00FF41"
        assert series.style.down_color == "#FF0040"


class TestAreaSeries:
    """Test AreaSeries class"""
    
    def test_initialization(self):
        """Test area series initialization"""
        series = AreaSeries("Area")
        
        assert series.name == "Area"
        assert series.visible == True
    
    def test_set_data(self):
        """Test setting area data"""
        series = AreaSeries()
        data = [
            {"time": datetime(2024, 1, 1), "value": 1000},
            {"time": datetime(2024, 1, 2), "value": 1100},
        ]
        
        series.set_data(data)
        assert len(series.data) == 2


class TestHistogramSeries:
    """Test HistogramSeries class"""
    
    def test_initialization(self):
        """Test histogram series initialization"""
        series = HistogramSeries("Volume")
        
        assert series.name == "Volume"
        assert series.visible == True
    
    def test_set_data(self):
        """Test setting histogram data"""
        series = HistogramSeries()
        data = [
            {"time": datetime(2024, 1, 1), "value": 1000000},
            {"time": datetime(2024, 1, 2), "value": 1500000},
        ]
        
        series.set_data(data)
        assert len(series.data) == 2


class TestSeriesDataRange:
    """Test data range calculations"""
    
    def test_line_series_price_range(self):
        """Test price range calculation for line series"""
        series = LineSeries()
        data = [
            {"time": datetime(2024, 1, 1), "value": 100},
            {"time": datetime(2024, 1, 2), "value": 150},
            {"time": datetime(2024, 1, 3), "value": 120},
        ]
        series.set_data(data)
        
        min_p, max_p = series._get_price_range(data)
        assert min_p == 100
        assert max_p == 150
    
    def test_candlestick_price_range(self):
        """Test price range calculation for candlesticks"""
        series = CandlestickSeries()
        data = [
            {
                "time": datetime(2024, 1, 1),
                "open": 100,
                "high": 105,
                "low": 95,
                "close": 102
            }
        ]
        series.set_data(data)
        
        min_p, max_p = series._get_price_range(data)
        assert min_p == 95
        assert max_p == 105
