# test_vispy_integration.py
import sys
import os

# Add the src directory to Python path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from PyQt5.QtWidgets import QApplication
    from vispy_chart import VispyChartWidget
    
    def main():
        app = QApplication(sys.argv)
        
        # Create the chart widget
        chart = VispyChartWidget()
        chart.setWindowTitle("Lightweight Charts Python - First Visual Test")
        chart.resize(800, 600)
        chart.show()
        
        print("✅ Chart window created successfully!")
        print("If you see a blank window, your Vispy + PyQt5 integration is working!")
        
        sys.exit(app.exec_())
    
    if __name__ == "__main__":
        main()

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you have PyQt5 and vispy installed:")
    print("pip install pyqt5 vispy numpy")
except Exception as e:
    print(f"❌ Error: {e}")