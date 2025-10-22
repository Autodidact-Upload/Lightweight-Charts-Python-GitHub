# Changelog

All notable changes to Lightweight Charts for Python will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-22

### Added
- **Core Features**
  - GPU-accelerated chart rendering with Vispy
  - Line, Candlestick, Area, and Histogram series types
  - Automatic time and price scaling with padding
  - Pan and zoom functionality
  - Real-time data update support
  - Chart export to PNG images

- **Multi-Pane System**
  - Independent panes with own price scales
  - Grid-based layout system
  - Synchronized crosshair across all panes
  - Visual border separators between panes
  - Y-axis locking for indicator panes

- **Technical Indicators**
  - Simple Moving Average (SMA)
  - Exponential Moving Average (EMA)
  - Weighted Moving Average (WMA)
  - Relative Strength Index (RSI)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands

- **Interactive Features**
  - Crosshair system with event callbacks
  - Visual crosshair rendering with lines following mouse
  - Price markers on price axis
  - Time markers on time axis
  - Mouse move and leave event subscriptions
  - Tooltip data extraction
  - Fullscreen and maximized window modes

- **Real-Time Integration**
  - WebSocket support for live data streaming
  - Kraken exchange integration example
  - HYBRID mode (OHLC + Trade feeds)
  - `series.update()` method for live candle updates
  - Background thread architecture for WebSocket
  - Historical data fetching via REST API

- **Data Validation**
  - Comprehensive data validation in all series types
  - Required field checking (time, value, OHLC)
  - Type checking for data inputs
  - Clear error messages for invalid data

- **Documentation**
  - Complete API reference (docs/API.md)
  - Step-by-step tutorial (docs/TUTORIAL.md)
  - Features guide (docs/FEATURES.md)
  - Multi-pane guide (docs/MULTI_PANE_GUIDE.md)
  - Project status (docs/PROJECT_STATUS.md)
  - Contributing guidelines (docs/CONTRIBUTING.md)
  - 17 comprehensive examples

- **Testing**
  - 18 test files for Chart, Series, and Scales
  - pytest configuration
  - Code coverage reporting

### Fixed
- **Python 3.8 Compatibility**
  - Fixed type hints using `list[Type]` syntax (Python 3.9+)
  - Now uses `List[Type]` from typing module
  - Tested and compatible with Python 3.8+

- **Data Validation**
  - Added validation to prevent empty data
  - Check for required fields in all series
  - Proper error messages for missing fields

- **Error Handling**
  - Silent failures replaced with logging
  - Try-catch blocks around visual operations
  - Graceful degradation when Vispy unavailable

### Changed
- **Project Structure**
  - Clean root directory with only essential files
  - Proper organization: src/, examples/, tests/, docs/
  - Configuration files in root (pyproject.toml, setup.py)
  - Documentation files in docs/

- **README.md**
  - Updated with correct feature list
  - Added real-time data integration section
  - Added multi-pane charts section
  - Improved installation instructions
  - Added comprehensive examples table

### Security
- Input validation prevents invalid data from causing crashes
- Type checking ensures data integrity

---

## [1.1.0] - Planned

### High Priority
- [ ] Fix real-time candle visual scaling
- [ ] Per-pane price scale labels
- [ ] Tooltip/legend system
- [ ] Time axis labels

### Medium Priority
- [ ] Interactive pane resizing
- [ ] Collapsible panes
- [ ] Save/load pane layouts
- [ ] More exchange integrations (Binance, Coinbase)

### Low Priority
- [ ] Volume profile visualization
- [ ] More chart types (Renko, Heikin-Ashi)
- [ ] Drawing tools
- [ ] WebGL backend for web

---

## Known Issues

### Real-Time Candle Formation
- **Issue**: Current forming candle updates but visual changes are minimal
- **Status**: Under investigation
- **Workaround**: Using high-volume pairs like BTC shows better movement

### Low-Volume Pairs
- **Issue**: PAXG/USD has infrequent trades
- **Impact**: Longer gaps between updates
- **Solution**: Trade feed provides updates when trades occur

---

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

**Maintained by:** Lightweight Charts Python Contributors  
**Inspired by:** [TradingView Lightweight Charts](https://github.com/tradingview/lightweight-charts)
