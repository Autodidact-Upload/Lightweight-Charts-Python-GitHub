# src/series/base_series.py
from __future__ import annotations
from typing import Optional, List, Any, Dict
from abc import ABC, abstractmethod

from ..delegates import Delegate
from ..time_data import TimePointIndex
from ..chart_model import ChartModel

class BaseSeries(ABC):
    """Base class for all series types - equivalent to TypeScript Series<T>"""
    
    def __init__(self, model: ChartModel, series_type: str):
        self._model = model
        self._series_type = series_type
        self._data: List[Any] = []
        
        # Events - integrate with your existing delegate system
        self.data_changed = Delegate()
        self.options_changed = Delegate()
    
    def set_data(self, data: List[Any]) -> None:
        """Python version of setData() from TypeScript"""
        self._data = data
        self.data_changed.emit()
        self._model.update_source(self)
        self._model.update_crosshair()
    
    def first_value(self) -> Optional[float]:
        """Get first value in visible range - used for price scaling"""
        if not self._data:
            return None
        # This will depend on your data structure
        return self._data[0].close  # Placeholder
    
    @abstractmethod
    def create_pane_views(self) -> List[Any]:
        """Create Vispy views for rendering - to be implemented by each series type"""
        pass
    
    @abstractmethod
    def bar_colorer(self) -> Any:
        """Get colorer for this series type"""
        pass

    # Core methods from TypeScript that we need to implement
    def price_line_color(self, last_bar_color: str) -> str:
        return last_bar_color  # Simplified for now
    
    def last_value_data(self, global_last: bool) -> Any:
        # Implementation needed
        pass
    
    def autoscale_info(self, start_time_point: TimePointIndex, end_time_point: TimePointIndex) -> Any:
        # Implementation needed  
        pass