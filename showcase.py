"""
Lightweight Charts Python - Complete Feature Showcase
Interactive demonstration of all implemented features

Run this script to see a menu of all features and examples.
"""

import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def print_header():
    """Print fancy header."""
    print("\n" + "="*80)
    print("🚀 LIGHTWEIGHT CHARTS PYTHON - FEATURE SHOWCASE")
    print("="*80)
    print("GPU-Accelerated Financial Charting with Multi-Pane Support")
    print("Version 1.0.0 | October 2025")
    print("="*80 + "\n")

def print_features():
    """Print completed features."""
    print("✅ COMPLETED FEATURES:")
    print("─" * 80)
    
    features = {
        "Core Charting": [
            "GPU-Accelerated Rendering (Vispy)",
            "Candlestick Charts (OHLC)",
            "Line Charts",
            "Area Charts with Fill",
            "Histogram/Bar Charts",
            "Time & Price Scales",
            "Pan & Zoom Interactivity",
        ],
        "Multi-Pane System ⭐ NEW": [
            "Independent Panes with Own Views",
            "Grid Layout Architecture",
            "Main Pane (Full Pan/Zoom)",
            "Indicator Panes (Y-Axis Locked)",
            "Synchronized Crosshair",
            "Visual Border Separators",
            "Customizable Height Ratios",
        ],
        "Crosshair System": [
            "Visual Crosshair Lines",
            "Multi-Pane Support",
            "Event Callbacks",
            "Customizable Colors",
        ],
        "Real-Time Data 🔴 LIVE": [
            "WebSocket Integration",
            "Kraken Exchange Support",
            "HYBRID Mode (OHLC + Trades)",
            "Live Candle Formation",
            "update() Method (TradingView-style)",
            "Background Threading",
            "Historical Data Fetching",
        ],
        "Technical Indicators": [
            "SMA (Simple Moving Average)",
            "EMA (Exponential Moving Average)",
            "WMA (Weighted Moving Average)",
            "RSI (Relative Strength Index)",
            "MACD (Moving Average Convergence Divergence)",
            "Bollinger Bands",
        ],
    }
    
    for category, items in features.items():
        print(f"\n📊 {category}")
        for item in items:
            print(f"   ✓ {item}")
    
    print("\n" + "─" * 80)

def print_examples():
    """Print available examples."""
    print("\n\n📁 AVAILABLE EXAMPLES (18 files):")
    print("─" * 80)
    
    examples = [
        ("1", "basic_line_chart.py", "Simple line chart", "⚡ Quick"),
        ("2", "candlestick_chart.py", "OHLC candlestick chart", "⚡ Quick"),
        ("3", "multiple_series.py", "Multiple series on one chart", "⚡ Quick"),
        ("4", "area_chart.py", "Area chart with fill", "⚡ Quick"),
        ("5", "volume_histogram.py", "Volume histogram bars", "⚡ Quick"),
        ("6", "advanced_styling.py", "Custom colors and dark theme", "🎨 Style"),
        ("7", "real_time_updates.py", "Streaming data updates", "🔄 Real-time"),
        ("8", "crosshair_markers.py", "Price and time markers", "🎯 Interactive"),
        ("9", "crosshair_interactive.py", "Interactive crosshair", "🎯 Interactive"),
        ("10", "indicators_complete.py", "All technical indicators", "📈 Advanced"),
        ("11", "fullscreen_chart.py", "Fullscreen mode", "🖥️ Display"),
        ("12", "maximized_window.py", "Maximized window", "🖥️ Display"),
        ("13", "multi_pane_simple.py", "Basic 2-pane chart", "✨ Multi-Pane"),
        ("14", "multi_pane_complete.py", "4-pane dashboard", "✨ Multi-Pane"),
        ("15", "multi_pane_chart.py", "Multi-pane (legacy)", "📜 Legacy"),
        ("16", "kraken_live_chart.py", "Live WebSocket PAXG/USD", "🔴 LIVE"),
        ("17", "kraken_realtime.py", "Real-time data demo", "🔴 LIVE"),
        ("18", "price_scale_demo.py", "Price scale demo", "📊 Demo"),
    ]
    
    for num, filename, desc, category in examples:
        print(f"{num:>3}. {filename:<30} - {desc:<35} [{category}]")
    
    print("─" * 80)

def print_project_stats():
    """Print project statistics."""
    print("\n\n📊 PROJECT STATISTICS:")
    print("─" * 80)
    
    stats = {
        "Source Files": "10 core modules",
        "Example Scripts": "18 comprehensive examples",
        "Documentation Files": "8 main docs + archives",
        "Test Files": "18 test modules",
        "Lines of Code": "~8,000+ lines",
        "Dependencies": "3 core (vispy, numpy, PyQt6)",
        "Performance": "10,000+ candles at 60 FPS",
        "Multi-Pane": "Up to 4 panes with no penalty",
    }
    
    for key, value in stats.items():
        print(f"  {key:<25} : {value}")
    
    print("─" * 80)

def print_architecture():
    """Print architecture overview."""
    print("\n\n🏗️  ARCHITECTURE:")
    print("─" * 80)
    print("""
Chart
├── Canvas (Vispy SceneCanvas)
└── Grid Layout
    ├── Pane 1 (Main) - Full interactivity
    │   ├── View + Camera
    │   ├── Crosshair Visual
    │   └── Series (Candles, Lines, etc.)
    ├── Pane 2 (Volume) - Y-locked
    │   ├── View + Camera (horizontal only)
    │   ├── Crosshair Visual
    │   └── Histogram Series
    └── Pane N (Indicators) - Y-locked
        ├── View + Camera (horizontal only)
        ├── Crosshair Visual
        └── Line Series (RSI, MACD, etc.)

Real-Time Data Flow:
WebSocket → Background Thread → Update Current Candle → 
series.update() → Timer (10 FPS) → Visual Update → GPU Render
    """)
    print("─" * 80)

def print_menu():
    """Print interactive menu."""
    print("\n\n🎮 INTERACTIVE MENU:")
    print("─" * 80)
    print("Choose what to run:")
    print()
    print("  [1-18] Run specific example (see list above)")
    print("  [Q]    Quick Demo - Multi-pane with indicators")
    print("  [L]    Live Demo - Real-time Kraken WebSocket")
    print("  [D]    Documentation - View project status")
    print("  [X]    Exit")
    print()
    print("─" * 80)

def run_example(number):
    """Run a specific example."""
    examples = {
        "1": "basic_line_chart.py",
        "2": "candlestick_chart.py",
        "3": "multiple_series.py",
        "4": "area_chart.py",
        "5": "volume_histogram.py",
        "6": "advanced_styling.py",
        "7": "real_time_updates.py",
        "8": "crosshair_markers.py",
        "9": "crosshair_interactive.py",
        "10": "indicators_complete.py",
        "11": "fullscreen_chart.py",
        "12": "maximized_window.py",
        "13": "multi_pane_simple.py",
        "14": "multi_pane_complete.py",
        "15": "multi_pane_chart.py",
        "16": "kraken_live_chart.py",
        "17": "kraken_realtime.py",
        "18": "price_scale_demo.py",
    }
    
    if number in examples:
        filename = examples[number]
        filepath = project_root / "examples" / filename
        
        if filepath.exists():
            print(f"\n🚀 Running: {filename}")
            print("─" * 80)
            os.system(f"python {filepath}")
        else:
            print(f"\n❌ Error: {filename} not found!")
    else:
        print("\n❌ Invalid example number!")

def show_documentation():
    """Show documentation."""
    print("\n\n📚 DOCUMENTATION:")
    print("─" * 80)
    print("""
Main Documentation:
  • README.md - Project overview
  • docs/PROJECT_STATUS.md - Current state and roadmap
  • docs/MULTI_PANE_GUIDE.md - Complete multi-pane guide (25+ examples)
  • docs/API.md - Complete API reference
  • docs/TUTORIAL.md - Step-by-step tutorial
  • docs/FEATURES.md - Feature documentation
  • docs/CONTRIBUTING.md - Development guidelines

Quick Start:
  1. Read README.md for overview
  2. Run: python examples/basic_line_chart.py
  3. Run: python examples/multi_pane_simple.py
  4. Run: python examples/kraken_live_chart.py (live data!)
  5. Explore other examples

Online Documentation:
  All docs are in the /docs directory
  Start with docs/PROJECT_STATUS.md for current state
    """)
    print("─" * 80)
    input("\nPress ENTER to continue...")

def show_known_issues():
    """Show known issues."""
    print("\n\n⚠️  KNOWN ISSUES:")
    print("─" * 80)
    print("""
1. Real-Time Candle Visual Scaling
   Status: Under investigation
   Issue: Current forming candle updates but visual changes are minimal
   Cause: Price scale auto-ranging causing small price changes to appear minimal
   Workaround: High-volume pairs like BTC show better movement

2. Low-Volume Pairs
   Status: Expected behavior
   Issue: PAXG/USD has infrequent trades
   Impact: Longer gaps between updates
   Solution: Trade feed provides updates when trades occur
    """)
    print("─" * 80)
    input("\nPress ENTER to continue...")

def main():
    """Main function."""
    print_header()
    print_features()
    print_examples()
    print_project_stats()
    print_architecture()
    
    while True:
        print_menu()
        
        choice = input("Enter your choice: ").strip().upper()
        
        if choice == 'X':
            print("\n👋 Thank you for exploring Lightweight Charts Python!")
            print("⭐ Star us on GitHub if you found this useful!")
            print()
            break
        elif choice == 'Q':
            run_example("14")  # Multi-pane complete
        elif choice == 'L':
            run_example("16")  # Kraken live
        elif choice == 'D':
            show_documentation()
        elif choice == 'I':
            show_known_issues()
        elif choice.isdigit() and 1 <= int(choice) <= 18:
            run_example(choice)
        else:
            print("\n❌ Invalid choice! Please try again.")
        
        print("\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
