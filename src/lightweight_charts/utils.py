"""
Utility functions for Lightweight Charts
"""

from typing import Tuple


def hex_to_rgb(hex_color: str) -> Tuple[float, float, float]:
    """
    Convert hex color code to RGB tuple (0.0-1.0 range).
    
    Args:
        hex_color: Color in hex format (e.g., "#2196F3")
    
    Returns:
        Tuple of (R, G, B) values in 0.0-1.0 range
    """
    hex_color = hex_color.lstrip('#').upper()
    if len(hex_color) == 6:
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return (r, g, b)
    elif len(hex_color) == 8:
        # Handle 8-char hex (with alpha, but we ignore alpha here)
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return (r, g, b)
    else:
        return (0.0, 0.0, 0.0)


def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> Tuple[float, float, float, float]:
    """
    Convert hex color to RGBA tuple.
    
    Args:
        hex_color: Color in hex format
        alpha: Alpha channel value (0.0-1.0)
    
    Returns:
        Tuple of (R, G, B, A) values
    """
    r, g, b = hex_to_rgb(hex_color)
    return (r, g, b, alpha)


def format_price(value: float, decimals: int = 2) -> str:
    """
    Format price value with appropriate scaling.
    
    Args:
        value: Price value
        decimals: Number of decimal places
    
    Returns:
        Formatted price string
    """
    if abs(value) >= 1e9:
        return f"${value / 1e9:.{decimals}f}B"
    elif abs(value) >= 1e6:
        return f"${value / 1e6:.{decimals}f}M"
    elif abs(value) >= 1e3:
        return f"${value / 1e3:.{decimals}f}K"
    else:
        return f"${value:.{decimals}f}"


def format_volume(volume: float) -> str:
    """Format volume with appropriate scaling."""
    if volume >= 1e9:
        return f"{volume / 1e9:.2f}B"
    elif volume >= 1e6:
        return f"{volume / 1e6:.2f}M"
    elif volume >= 1e3:
        return f"{volume / 1e3:.2f}K"
    else:
        return f"{volume:.0f}"


def normalize_value(value: float, min_val: float, max_val: float) -> float:
    """
    Normalize value to range [-1, 1].
    
    Args:
        value: Value to normalize
        min_val: Minimum value in range
        max_val: Maximum value in range
    
    Returns:
        Normalized value in [-1, 1]
    """
    if max_val == min_val:
        return 0.0
    return (value - min_val) / (max_val - min_val) * 2 - 1


def denormalize_value(normalized: float, min_val: float, max_val: float) -> float:
    """
    Convert normalized value back to original range.
    
    Args:
        normalized: Value in [-1, 1] range
        min_val: Minimum value in original range
        max_val: Maximum value in original range
    
    Returns:
        Value in original range
    """
    return (normalized + 1) / 2 * (max_val - min_val) + min_val


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value to range [min_val, max_val]."""
    return max(min_val, min(max_val, value))
