"""
Unit tests for Scale classes
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lightweight_charts import TimeScale, PriceScale


class TestTimeScale:
    """Test TimeScale class"""
    
    def test_initialization(self):
        """Test time scale initialization"""
        scale = TimeScale()
        
        assert len(scale.data) == 0
        assert scale.visible_range == (0, 0)
    
    def test_set_data(self):
        """Test setting data"""
        data = [
            {"time": datetime(2024, 1, 1), "value": 100},
            {"time": datetime(2024, 1, 2), "value": 102},
            {"time": datetime(2024, 1, 3), "value": 101},
        ]
        scale = TimeScale(data)
        
        assert len(scale.data) == 3
        assert scale.visible_range == (0, 2)
    
    def test_get_visible_data(self):
        """Test getting visible data"""
        data = [
            {"time": datetime(2024, 1, i+1), "value": 100 + i}
            for i in range(10)
        ]
        scale = TimeScale(data)
        scale.set_visible_range(2, 7)
        
        visible = scale.get_visible_data()
        assert len(visible) == 6
        assert visible[0]["value"] == 102
    
    def test_set_visible_range(self):
        """Test setting visible range"""
        data = [{"time": datetime(2024, 1, i+1), "value": i} for i in range(10)]
        scale = TimeScale(data)
        
        scale.set_visible_range(3, 7)
        assert scale.visible_range == (3, 7)
    
    def test_visible_range_bounds(self):
        """Test that visible range respects data bounds"""
        data = [{"time": datetime(2024, 1, i+1), "value": i} for i in range(10)]
        scale = TimeScale(data)
        
        # Test negative bounds
        scale.set_visible_range(-5, 15)
        assert scale.visible_range[0] >= 0
        assert scale.visible_range[1] <= 9
    
    def test_zoom(self):
        """Test zooming"""
        data = [{"time": datetime(2024, 1, i+1), "value": i} for i in range(31)]  # Only 31 days in January
        scale = TimeScale(data)
        scale.set_visible_range(0, 30)
        
        # Zoom in
        scale.zoom(2.0)
        start, end = scale.visible_range
        range_size = end - start
        assert range_size < 30  # Should be smaller
    
    def test_pan(self):
        """Test panning"""
        data = [{"time": datetime(2024, 1, i+1), "value": i} for i in range(31)]  # Only 31 days in January
        scale = TimeScale(data)
        scale.set_visible_range(0, 20)
        
        # Pan right
        scale.pan(5)
        assert scale.visible_range[0] >= 5


class TestPriceScale:
    """Test PriceScale class"""
    
    def test_initialization(self):
        """Test price scale initialization"""
        scale = PriceScale()
        
        assert scale.auto_scale == True
        assert scale.min_value == 0.0
        assert scale.max_value == 100.0
    
    def test_update_range(self):
        """Test updating price range"""
        scale = PriceScale()
        scale.update_range(50, 150)
        
        assert scale.min_value < 50
        assert scale.max_value > 150
    
    def test_update_range_no_padding(self):
        """Test update range without padding"""
        scale = PriceScale()
        scale.update_range(50, 150, auto_pad=False)
        
        assert scale.min_value == 50
        assert scale.max_value == 150
    
    def test_get_labels(self):
        """Test label generation"""
        scale = PriceScale()
        scale.update_range(0, 100, auto_pad=False)
        labels = scale.get_labels(5)
        
        assert len(labels) == 5
        assert all(isinstance(label, tuple) for label in labels)
    
    def test_price_conversion(self):
        """Test price to/from normalized coordinate"""
        scale = PriceScale()
        scale.update_range(0, 100, auto_pad=False)
        
        # Test middle
        y = scale.get_y_at_price(50)
        assert -1 <= y <= 1
        
        # Convert back
        price = scale.get_price_at_y(y)
        assert abs(price - 50) < 1
    
    def test_format_price(self):
        """Test price formatting"""
        # Large values
        formatted = PriceScale._format_price(1.5e9)
        assert "B" in formatted
        
        # Medium values
        formatted = PriceScale._format_price(1.5e6)
        assert "M" in formatted
        
        # Thousands
        formatted = PriceScale._format_price(1500)
        assert "K" in formatted
        
        # Small values
        formatted = PriceScale._format_price(50)
        assert "$" in formatted
    
    def test_set_padding(self):
        """Test setting custom padding"""
        scale = PriceScale()
        scale.set_padding(0.1)
        
        assert scale._padding == 0.1
        
        # Test boundary
        scale.set_padding(2.0)  # Should clamp to 1.0
        assert scale._padding == 1.0
