# Contributing to Lightweight Charts for Python

## Welcome!

I appreciate your interest in contributing to this project. This document provides guidelines for contributing.

## Getting Started

1. **Fork the repository**
2. **Clone your fork:**
   ```bash
   git clone https://github.com/yourusername/Lightweight-Charts-Python.git
   cd Lightweight-Charts-Python
   ```

3. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

4. **Install development dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov black flake8
   ```

---

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/my-feature
```

### 2. Make Your Changes

- Follow PEP 8 style guidelines
- Write clear, descriptive commit messages
- Add tests for new features

### 3. Run Tests

```bash
pytest tests/
```

### 4. Check Code Quality

```bash
# Format code
black src/

# Check for issues
flake8 src/
```

### 5. Submit a Pull Request

- Describe your changes clearly
- Reference any related issues
- Ensure all tests pass

---

## Code Style

### Python Style Guide

We follow PEP 8. Key points:

```python
# Good
def add_line_series(name: str = "", style: Optional[LineStyleOptions] = None) -> LineSeries:
    """Add a line series to the chart."""
    series = LineSeries(name, style)
    return series

# Avoid
def addLineSeries(name="", style=None):
    s=LineSeries(name,style)
    return s
```

### Type Hints

Always use type hints:

```python
from typing import List, Optional, Dict, Tuple

def process_data(
    data: List[Dict[str, float]],
    limit: int = 100
) -> Tuple[float, float]:
    """Process data and return min/max."""
    pass
```

### Documentation

Use docstrings for all public functions:

```python
def set_data(self, data: List[Dict[str, Any]]):
    """
    Set series data.
    
    Args:
        data: List of data points (dicts or dataclass objects)
    
    Raises:
        ValueError: If data is empty
    """
    if not data:
        raise ValueError("Data cannot be empty")
    self.data = data
```

---

## Adding New Features

### Adding a New Series Type

1. **Create new class in `series.py`:**

```python
class MySeries(BaseSeries):
    """My new series type."""
    
    def __init__(self, name: str = "", style: Optional[MyStyleOptions] = None):
        super().__init__(name)
        self.style = style or MyStyleOptions()
        self.visual = None
    
    def create_visual(self, view):
        """Create Vispy visual."""
        # Implementation
        pass
    
    def update_visual(self, time_scale: TimeScale, price_scale: PriceScale):
        """Update visual with data."""
        # Implementation
        pass
```

2. **Add method in `chart.py`:**

```python
def add_my_series(
    self,
    name: str = "",
    style: Optional[MyStyleOptions] = None
) -> MySeries:
    """Add my series to chart."""
    series = MySeries(name, style)
    series.create_visual(self.view)
    self.series[name or f"my_{len(self.series)}"] = series
    return series
```

3. **Add data type in `data_types.py`:**

```python
@dataclass
class MyStyleOptions:
    """Configuration for my series."""
    color: str = "#2196F3"
    width: int = 2
```

4. **Update `__init__.py`:**

```python
from .series import MySeries
from .data_types import MyStyleOptions

__all__ = [
    # ... existing exports
    "MySeries",
    "MyStyleOptions",
]
```

5. **Create tests in `tests/`:**

```python
def test_my_series():
    """Test my series."""
    series = MySeries("test")
    assert series.name == "test"
    assert series.visible == True
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_chart.py

# Run with coverage
pytest --cov=src
```

### Writing Tests

```python
# tests/test_my_feature.py
import pytest
from src.lightweight_charts import Chart, MySeries

class TestMySeries:
    
    def test_initialization(self):
        """Test series initialization."""
        series = MySeries("test")
        assert series.name == "test"
        assert series.visible == True
    
    def test_set_data(self):
        """Test setting data."""
        series = MySeries()
        data = [{"time": ..., "value": 100}]
        series.set_data(data)
        assert len(series.data) == 1
    
    def test_invalid_data(self):
        """Test error handling."""
        series = MySeries()
        with pytest.raises(ValueError):
            series.set_data([])
```

---

## Documentation

### Update API Documentation

If you add new features, update `/docs/API.md`:

```markdown
### `MyNewClass`

Description of the class.

#### Constructor

```python
MyNewClass(param1: str, param2: int = 10)
```

#### Methods

##### `method_name()`

Description of method.
```

---

## Bug Reports

### Creating an Issue

1. Check if issue already exists
2. Include:
   - Python version
   - Vispy version
   - Operating system
   - Minimal reproducible example
   - Expected vs actual behavior

### Example

```
**Bug:** Chart doesn't render candlesticks

**Environment:**
- Python 3.9
- Vispy 0.9.0
- Windows 10

**Steps to reproduce:**
1. Create chart
2. Add candlestick series
3. Call render()

**Expected:** Candlesticks should appear
**Actual:** Chart window is blank

**Code:**
```python
chart = Chart()
candles = chart.add_candlestick_series()
candles.set_data([...])
chart.render()
```
```

---

## Feature Requests

Describe the feature, why it's useful, and how it should work.

---

## Commit Message Guidelines

```
# Good commit messages

feat: Add RSI indicator
fix: Correct candlestick wick rendering
docs: Update API documentation
refactor: Optimize data scaling
test: Add tests for PriceScale

# Avoid
updated stuff
bug fixes
changes
```

---

## Pull Request Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No breaking changes (or documented)
- [ ] Works on Windows/Mac/Linux

---

## Project Structure

```
src/lightweight_charts/
├── __init__.py          # Package exports
├── chart.py             # Main Chart class
├── series.py            # Series implementations
├── scales.py            # TimeScale and PriceScale
├── data_types.py        # Data structures and configs
├── utils.py             # Utility functions
└── renderers.py         # (Future) Advanced rendering

tests/
├── test_chart.py        # Chart tests
├── test_series.py       # Series tests
└── test_scales.py       # Scale tests

examples/
├── basic_line_chart.py
├── candlestick_chart.py
└── ...

docs/
├── API.md               # API Reference
├── TUTORIAL.md          # Tutorial
└── CONTRIBUTING.md      # This file
```

---

## Questions?

- Open an issue on GitHub
- Check existing documentation
- Review example code

Thank you for contributing!
