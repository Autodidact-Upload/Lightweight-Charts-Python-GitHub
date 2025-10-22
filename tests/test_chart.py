"""
Unit tests for Chart class
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lightweight_charts import Chart, LineStyleOptions, CandleStickStyleOptions


class TestChart:
    """Test Chart class"""
    
    def test_chart_initialization(self):
        """Test chart creation with default parameters"""
        chart = Chart()
        assert chart.width == 800
        assert chart.height == 600
        assert chart.title == "Financial Chart"
    
    def test_chart_custom_initialization(self):
        """Test chart creation with custom parameters"""
        chart = Chart(
            width=1200,
            height=800,
            title="My Chart",
            background_color="#1e1e1e"
        )
        assert chart.width == 1200
        assert chart.height == 800
        assert chart.title == "My Chart"
    
    def test_add_line_series(self):
        """Test adding line series"""
        chart = Chart()
        line = chart.add_line_series("Test Line")
        
        assert "Test Line" in chart.series
        assert chart.series["Test Line"].name == "Test Line"
    
    def test_add_candlestick_series(self):
        """Test adding candlestick series"""
        chart = Chart()
        candles = chart.add_candlestick_series("OHLC")
        
        assert "OHLC" in chart.series
        assert chart.series["OHLC"].name == "OHLC"
    
    def test_add_area_series(self):
        """Test adding area series"""
        chart = Chart()
        area = chart.add_area_series("Area")
        
        assert "Area" in chart.series
        assert chart.series["Area"].name == "Area"
    
    def test_add_histogram_series(self):
        """Test adding histogram series"""
        chart = Chart()
        hist = chart.add_histogram_series("Histogram")
        
        assert "Histogram" in chart.series
        assert chart.series["Histogram"].name == "Histogram"
    
    def test_get_series(self):
        """Test getting series by name"""
        chart = Chart()
        line = chart.add_line_series("My Line")
        retrieved = chart.get_series("My Line")
        
        assert retrieved is not None
        assert retrieved.name == "My Line"
    
    def test_get_nonexistent_series(self):
        """Test getting non-existent series"""
        chart = Chart()
        series = chart.get_series("Nonexistent")
        
        assert series is None
    
    def test_remove_series(self):
        """Test removing series"""
        chart = Chart()
        chart.add_line_series("Test")
        
        result = chart.remove_series("Test")
        assert result == True
        assert "Test" not in chart.series
    
    def test_remove_nonexistent_series(self):
        """Test removing non-existent series"""
        chart = Chart()
        result = chart.remove_series("Nonexistent")
        
        assert result == False
    
    def test_set_series_visible(self):
        """Test toggling series visibility"""
        chart = Chart()
        chart.add_line_series("Test")
        
        chart.set_series_visible("Test", False)
        assert chart.series["Test"].visible == False
        
        chart.set_series_visible("Test", True)
        assert chart.series["Test"].visible == True
    
    def test_clear_series(self):
        """Test clearing all series"""
        chart = Chart()
        chart.add_line_series("Line1")
        chart.add_line_series("Line2")
        chart.add_line_series("Line3")
        
        chart.clear_series()
        assert len(chart.series) == 0
    
    def test_set_background_color(self):
        """Test setting background color"""
        chart = Chart()
        chart.set_background_color("#FF0000")
        
        assert chart.background_color == (1.0, 0.0, 0.0)
    
    def test_get_chart_size(self):
        """Test getting chart size"""
        chart = Chart(width=1200, height=800)
        size = chart.get_chart_size()
        
        assert size == (1200, 800)
    
    def test_multiple_series(self):
        """Test adding multiple series"""
        chart = Chart()
        chart.add_line_series("Line1")
        chart.add_line_series("Line2")
        chart.add_candlestick_series("Candles")
        
        assert len(chart.series) == 3
        assert "Line1" in chart.series
        assert "Line2" in chart.series
        assert "Candles" in chart.series


class TestChartData:
    """Test chart data handling"""
    
    def setup_method(self):
        """Setup for each test"""
        self.chart = Chart()
        self.sample_data = [
            {"time": datetime(2024, 1, 1), "value": 100},
            {"time": datetime(2024, 1, 2), "value": 102},
            {"time": datetime(2024, 1, 3), "value": 101},
        ]
    
    def test_set_line_data(self):
        """Test setting data on line series"""
        line = self.chart.add_line_series("Test")
        line.set_data(self.sample_data)
        
        assert len(line.data) == 3
        assert line.data[0]["value"] == 100
    
    def test_set_ohlc_data(self):
        """Test setting OHLC data"""
        ohlc_data = [
            {
                "time": datetime(2024, 1, 1),
                "open": 100,
                "high": 102,
                "low": 99,
                "close": 101
            }
        ]
        
        candles = self.chart.add_candlestick_series("OHLC")
        candles.set_data(ohlc_data)
        
        assert len(candles.data) == 1
        assert candles.data[0]["close"] == 101
    
    def test_update_time_scale(self):
        """Test updating time scale"""
        self.chart.update_time_scale_data(self.sample_data)
        
        assert len(self.chart.time_scale.data) == 3
