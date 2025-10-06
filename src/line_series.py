# src/series/line_series.py
from __future__ import annotations
from typing import List, Any, Dict  # Import the required types
from .base_series import BaseSeries
from ..chart_model import ChartModel

class LineSeries(BaseSeries):
    """First concrete series implementation"""
    
    def __init__(self, model: ChartModel):  # The type hint for 'model' should be ChartModel
        super().__init__(model, 'line')
    
    def create_pane_views(self) -> List[Any]:  # Now List and Any are defined
        """Create Vispy line series view"""
        # This will connect to your Vispy rendering
        from ..views.line_series_view import LineSeriesView
        return [LineSeriesView(self)]
    
    def bar_colorer(self) -> Any:  # Now Any is defined
        from ..colorers.line_colorer import LineColorer
        return LineColorer(self)