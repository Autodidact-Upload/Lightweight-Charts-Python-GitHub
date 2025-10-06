# src/vispy_chart.py
from __future__ import annotations
from typing import Optional
import numpy as np

from PyQt5.QtWidgets import QWidget, QVBoxLayout
import vispy.app
import vispy.scene
from vispy.scene import SceneCanvas

from .chart_model import ChartModel
from .time_scale import TimeScale
from .price_scale import PriceScale

class VispyChartWidget(QWidget):
    """
    Main chart widget that bridges your core engine with Vispy rendering.
    This is where your chart becomes visible!
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Initialize your core chart engine
        self._chart_model = ChartModel()
        self._time_scale = TimeScale(self._chart_model)
        self._price_scale = PriceScale(self._chart_model)
        
        # Create Vispy canvas
        self._canvas = SceneCanvas(size=(800, 600), show=True)
        self._view = self._canvas.central_widget.add_view()
        
        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self._canvas.native)
        self.setLayout(layout)
        
        # Connect events between your engine and Vispy
        self._connect_events()
        
    def _connect_events(self) -> None:
        """Connect your chart model events to Vispy updates"""
        self._chart_model.update_delegate.connect(self._on_chart_update)
        self._chart_model.crosshair_moved.connect(self._on_crosshair_move)
        
    def _on_chart_update(self) -> None:
        """Called when chart data or ranges change"""
        # This will trigger all series to update their Vispy visuals
        self._update_all_visuals()
        
    def _on_crosshair_move(self, x: float, y: float) -> None:
        """Handle crosshair movement"""
        # Convert coordinates and update crosshair visual
        pass
        
    def _update_all_visuals(self) -> None:
        """Update all Vispy visuals when chart changes"""
        # This will iterate through all series and update their Vispy representations
        pass
    
    @property
    def chart_model(self) -> ChartModel:
        """Access to the core chart model"""
        return self._chart_model
    
    @property 
    def time_scale(self) -> TimeScale:
        """Access to time scale"""
        return self._time_scale
    
    @property
    def price_scale(self) -> PriceScale:
        """Access to price scale"""
        return self._price_scale
    
    def add_line_series(self):
        """Add a line series to the chart"""
        from .series.line_series import LineSeries
        line_series = LineSeries(self._chart_model)
        # This will eventually create and manage Vispy line visuals
        return line_series