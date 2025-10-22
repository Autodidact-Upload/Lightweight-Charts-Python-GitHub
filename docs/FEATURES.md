# ✨ Features Guide

**Lightweight Charts for Python - Advanced Features**

This guide covers the advanced display modes, theming, and interactive features available in the library.

---

## 📺 Display Modes

### **1. Normal Window (Default)**

Standard window with fixed dimensions.

```python
from lightweight_charts import Chart

chart = Chart(
    width=1200,
    height=600,
    title="Trading Chart"
)
chart.render()
```

**Best for:** Development, testing, embedded applications

---

### **2. Maximized Window** ⭐ **RECOMMENDED**

Window fills the screen but keeps title bar and window controls (close, minimize, maximize buttons).

```python
chart = Chart(
    title="Trading Dashboard",
    background_color="#1e1e1e",
    maximized=True  # Fills screen, keeps controls
)
chart.render()
```

**Command line:**
```bash
python examples/crosshair_interactive.py           # Maximized by default
python examples/crosshair_interactive.py -m        # Explicit maximized
```

**Features:**
- ✅ Window fills screen (~95% of height)
- ✅ Title bar visible
- ✅ Close/minimize/maximize buttons available
- ✅ Can resize and move window
- ✅ Easy to close

**Best for:** Daily trading, analysis, normal usage

---

### **3. Fullscreen Mode**

True fullscreen with no window borders or controls.

```python
chart = Chart(
    title="Trading Chart",
    fullscreen=True  # No borders, no controls
)
chart.render()
```

**Command line:**
```bash
python examples/crosshair_interactive.py --fullscreen
python examples/fullscreen_chart.py
```

**Features:**
- ✅ Uses 100% of screen space
- ❌ No title bar
- ❌ No window controls
- ⌨️ Press ESC or F11 to exit

**Best for:** Presentations, kiosk mode, immersive analysis

---

## 🎨 Dark Mode & Theming

Professional dark theme example:

```python
chart = Chart(
    background_color="#0a0a0a",  # Almost black
    maximized=True
)

# Neon green/pink candlesticks
chart.add_candlestick_series(
    "BTC/USD",
    CandleStickStyleOptions(
        up_color="#00FF41",       # Neon green (bull)
        down_color="#FF0040",     # Hot pink (bear)
        wick_color="#FFFFFF",     # White wicks
        border_up_color="#00FF41",
        border_down_color="#FF0040"
    )
)

# Gold moving average
chart.add_line_series(
    "MA20",
    LineStyleOptions(color="#FFD700", width=2)  # Gold
)

# Gray crosshair (subtle but visible)
chart.set_crosshair_colors(
    vert_color="#888888",
    horiz_color="#888888"
)
```

---

## 🎯 Interactive Crosshair

### **Visual Crosshair Lines**

The crosshair displays vertical and horizontal lines that follow your mouse:

```python
from lightweight_charts import Chart

chart = Chart(maximized=True)

# Crosshair is enabled by default!
line = chart.add_line_series("Price")
line.set_data(data)

chart.render()  # Move mouse to see crosshair
```

**Features:**
- ✅ Vertical line (time axis)
- ✅ Horizontal line (price axis)
- ✅ Follows mouse in real-time
- ✅ Snaps to nearest data point
- ✅ Hides when mouse leaves chart

---

### **Crosshair Event Callbacks**

Get data at cursor position:

```python
def on_crosshair_move(position):
    """Called when mouse moves over chart"""
    if position.series_data:
        print(f"Time: {position.time}")
        print(f"Price: ${position.price:.2f}")
        
        # For candlestick data
        if "close" in position.series_data:
            data = position.series_data
            print(f"Open: ${data['open']:.2f}")
            print(f"High: ${data['high']:.2f}")
            print(f"Low: ${data['low']:.2f}")
            print(f"Close: ${data['close']:.2f}")

def on_crosshair_leave():
    """Called when mouse leaves chart"""
    print("Mouse left chart area")

# Subscribe to events
chart.subscribe_crosshair_move(on_crosshair_move)
chart.subscribe_crosshair_leave(on_crosshair_leave)
```

---

## 🎮 Pan & Zoom

### **Mouse Controls**

Enabled by default:
- **Pan:** Click and drag
- **Zoom:** Mouse wheel

---

### **Programmatic Control**

```python
# Pan chart (positive = right, negative = left)
chart.pan(10)  # Pan 10 bars to the right

# Zoom (>1 = zoom in, <1 = zoom out)
chart.zoom(1.5)  # Zoom in 1.5x

# Zoom centered at specific point (0-1, where 0.5 = middle)
chart.zoom(2.0, center=0.5)  # Zoom in 2x at center
```

---

## 📸 Export Charts

### **Save as PNG**

```python
# Render chart
chart.render()

# Export to file
chart.export_image("chart_output.png")
```

**Requirements:**
```bash
pip install pillow  # For PNG export
```

---

## 📚 See Also

- **[API Reference](API.md)** - Complete API documentation
- **[Tutorial](TUTORIAL.md)** - Step-by-step guide
- **[Examples](../examples/)** - 17 working examples

---

*Last updated: October 22, 2025*  
*All features tested and working*
