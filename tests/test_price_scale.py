"""
Test Price Scale Visual Implementation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from lightweight_charts import (
    Chart,
    PriceScale,
    PriceScaleOptions,
    PriceScaleMode,
    PriceScaleMargins
)
from lightweight_charts.price_scale_visual import PriceScaleVisual


def test_price_scale_mode_enum():
    """Test PriceScaleMode enum values."""
    assert PriceScaleMode.NORMAL.value == "normal"
    assert PriceScaleMode.LOGARITHMIC.value == "logarithmic"
    assert PriceScaleMode.PERCENTAGE.value == "percentage"
    assert PriceScaleMode.INDEXED_TO_100.value == "indexed_to_100"


def test_price_scale_margins():
    """Test PriceScaleMargins configuration."""
    # Default margins
    margins = PriceScaleMargins()
    assert margins.top == 0.2
    assert margins.bottom == 0.1
    
    # Custom margins
    margins = PriceScaleMargins(top=0.3, bottom=0.15)
    assert margins.top == 0.3
    assert margins.bottom == 0.15
    
    # Out of range values should be clamped
    margins = PriceScaleMargins(top=1.5, bottom=-0.5)
    assert margins.top == 1.0  # Clamped to max
    assert margins.bottom == 0.0  # Clamped to min


def test_price_scale_options_defaults():
    """Test default PriceScaleOptions values."""
    opts = PriceScaleOptions()
    
    assert opts.auto_scale == True
    assert opts.mode == PriceScaleMode.NORMAL
    assert opts.invert_scale == False
    assert opts.align_labels == True
    assert opts.border_visible == True
    assert opts.border_color == "#2B2B43"
    assert opts.text_color == "#D1D4DC"
    assert opts.visible == True
    assert opts.ticks_visible == False
    assert opts.entire_text_only == False
    assert opts.minimum_width == 50


def test_price_scale_options_custom():
    """Test custom PriceScaleOptions configuration."""
    opts = PriceScaleOptions(
        auto_scale=False,
        mode=PriceScaleMode.LOGARITHMIC,
        invert_scale=True,
        border_color="#FF0000",
        text_color="#00FF00",
        visible=False,
        ticks_visible=True,
        minimum_width=100
    )
    
    assert opts.auto_scale == False
    assert opts.mode == PriceScaleMode.LOGARITHMIC
    assert opts.invert_scale == True
    assert opts.border_color == "#FF0000"
    assert opts.text_color == "#00FF00"
    assert opts.visible == False
    assert opts.ticks_visible == True
    assert opts.minimum_width == 100


def test_chart_price_scale_integration():
    """Test price scale integration with Chart class."""
    chart = Chart(width=800, height=600)
    
    # Price scale options should be initialized
    assert chart.price_scale_options is not None
    assert isinstance(chart.price_scale_options, PriceScaleOptions)
    
    # Price scale visual should not be created until render
    assert chart.price_scale_visual is None
    assert chart._price_scale_initialized == False


def test_chart_configure_price_scale():
    """Test configuring price scale on chart."""
    chart = Chart(width=800, height=600)
    
    # Configure with custom options
    custom_opts = PriceScaleOptions(
        border_color="#FFFF00",
        ticks_visible=True,
        minimum_width=80
    )
    
    chart.configure_price_scale(custom_opts)
    
    # Options should be updated
    assert chart.price_scale_options.border_color == "#FFFF00"
    assert chart.price_scale_options.ticks_visible == True
    assert chart.price_scale_options.minimum_width == 80


def test_chart_price_scale_width():
    """Test price scale width getters and setters."""
    chart = Chart(width=800, height=600)
    
    # Width should be 0 before initialization
    assert chart.get_price_scale_width() == 0  # type: ignore[attr-defined]
    
    # Setting width before initialization should not crash
    chart.set_price_scale_width(100)  # type: ignore[attr-defined]  # Should handle gracefully


def test_price_scale_label_generation():
    """Test price label generation for different modes."""
    price_scale = PriceScale()
    price_scale.update_range(1000, 5000)
    
    # Normal mode labels
    labels = price_scale.get_labels(num_labels=5)
    assert len(labels) == 5
    
    # All labels should be (value, string) tuples
    for value, text in labels:
        assert isinstance(value, float)
        assert isinstance(text, str)
        assert "$" in text  # Should have dollar sign


def test_price_scale_formatting():
    """Test price formatting for different magnitudes."""
    # Small values
    formatted = PriceScale._format_price(50.25)
    assert formatted == "$50.25"
    
    # Thousands
    formatted = PriceScale._format_price(5000)
    assert "K" in formatted
    
    # Millions
    formatted = PriceScale._format_price(5000000)
    assert "M" in formatted
    
    # Billions
    formatted = PriceScale._format_price(5000000000)
    assert "B" in formatted


def test_price_scale_modes_exist():
    """Test that all price scale modes are accessible."""
    modes = [
        PriceScaleMode.NORMAL,
        PriceScaleMode.LOGARITHMIC,
        PriceScaleMode.PERCENTAGE,
        PriceScaleMode.INDEXED_TO_100
    ]
    
    # Should be able to create options with each mode
    for mode in modes:
        opts = PriceScaleOptions(mode=mode)
        assert opts.mode == mode


if __name__ == "__main__":
    # Run tests
    print("Running Price Scale Tests...")
    print("=" * 60)
    
    test_price_scale_mode_enum()
    print("✅ Price scale mode enum test passed")
    
    test_price_scale_margins()
    print("✅ Price scale margins test passed")
    
    test_price_scale_options_defaults()
    print("✅ Price scale options defaults test passed")
    
    test_price_scale_options_custom()
    print("✅ Price scale options custom test passed")
    
    test_chart_price_scale_integration()
    print("✅ Chart integration test passed")
    
    test_chart_configure_price_scale()
    print("✅ Configure price scale test passed")
    
    test_chart_price_scale_width()
    print("✅ Price scale width test passed")
    
    test_price_scale_label_generation()
    print("✅ Label generation test passed")
    
    test_price_scale_formatting()
    print("✅ Price formatting test passed")
    
    test_price_scale_modes_exist()
    print("✅ Price scale modes test passed")
    
    print("=" * 60)
    print("🎉 ALL TESTS PASSED!")
