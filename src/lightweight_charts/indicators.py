"""
Technical Indicators for Lightweight Charts
Calculations for common trading indicators
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime


class IndicatorCalculator:
    """Base class for indicator calculations"""
    
    @staticmethod
    def extract_values(data: List[Dict[str, Any]], source: str = "close") -> np.ndarray:
        """
        Extract values from OHLC data.
        
        Args:
            data: List of OHLC data points
            source: Which value to extract (open, high, low, close, volume)
        
        Returns:
            NumPy array of values
        """
        values = []
        for item in data:
            if isinstance(item, dict):
                values.append(float(item.get(source, 0)))
            else:
                values.append(float(getattr(item, source, 0)))
        return np.array(values)
    
    @staticmethod
    def get_time(item: Union[Dict[str, Any], Any]) -> datetime:
        """
        Extract time from data item (dict or object).
        
        Args:
            item: Data point (dict or dataclass)
        
        Returns:
            datetime object
        """
        if isinstance(item, dict):
            return item["time"]
        else:
            return item.time


class MovingAverage(IndicatorCalculator):
    """Moving Average calculations (SMA, EMA, WMA)"""
    
    @staticmethod
    def sma(data: List[Dict[str, Any]], period: int = 20, source: str = "close") -> List[Dict[str, Any]]:
        """
        Simple Moving Average.
        
        Args:
            data: OHLC data
            period: Number of periods
            source: Data source (close, open, high, low)
        
        Returns:
            List of {time, value} dictionaries
        """
        values = MovingAverage.extract_values(data, source)
        result = []
        
        for i in range(len(values)):
            if i < period - 1:
                # Not enough data yet
                result.append({
                    "time": MovingAverage.get_time(data[i]),
                    "value": np.nan
                })
            else:
                # Calculate SMA
                window = values[i - period + 1:i + 1]
                sma_value = np.mean(window)
                result.append({
                    "time": MovingAverage.get_time(data[i]),
                    "value": float(sma_value)
                })
        
        return result
    
    @staticmethod
    def ema(data: List[Dict[str, Any]], period: int = 20, source: str = "close") -> List[Dict[str, Any]]:
        """
        Exponential Moving Average.
        
        Args:
            data: OHLC data
            period: Number of periods
            source: Data source
        
        Returns:
            List of {time, value} dictionaries
        """
        values = MovingAverage.extract_values(data, source)
        result = []
        
        # EMA multiplier
        multiplier = 2 / (period + 1)
        
        # Start with SMA for first value
        ema_value = np.mean(values[:period])
        
        for i in range(len(values)):
            if i < period - 1:
                result.append({
                    "time": MovingAverage.get_time(data[i]),
                    "value": np.nan
                })
            elif i == period - 1:
                result.append({
                    "time": MovingAverage.get_time(data[i]),
                    "value": float(ema_value)
                })
            else:
                # Calculate EMA: (Close - EMA(previous)) * multiplier + EMA(previous)
                ema_value = (values[i] - ema_value) * multiplier + ema_value
                result.append({
                    "time": MovingAverage.get_time(data[i]),
                    "value": float(ema_value)
                })
        
        return result
    
    @staticmethod
    def wma(data: List[Dict[str, Any]], period: int = 20, source: str = "close") -> List[Dict[str, Any]]:
        """
        Weighted Moving Average.
        
        Args:
            data: OHLC data
            period: Number of periods
            source: Data source
        
        Returns:
            List of {time, value} dictionaries
        """
        values = MovingAverage.extract_values(data, source)
        result = []
        
        # Create weights (more recent = higher weight)
        weights = np.arange(1, period + 1)
        
        for i in range(len(values)):
            if i < period - 1:
                result.append({
                    "time": MovingAverage.get_time(data[i]),
                    "value": np.nan
                })
            else:
                window = values[i - period + 1:i + 1]
                wma_value = np.sum(window * weights) / np.sum(weights)
                result.append({
                    "time": MovingAverage.get_time(data[i]),
                    "value": float(wma_value)
                })
        
        return result


class RSI(IndicatorCalculator):
    """Relative Strength Index"""
    
    @staticmethod
    def calculate(data: List[Dict[str, Any]], period: int = 14, source: str = "close") -> List[Dict[str, Any]]:
        """
        Calculate RSI.
        
        Args:
            data: OHLC data
            period: RSI period (typically 14)
            source: Data source
        
        Returns:
            List of {time, value} dictionaries with RSI values (0-100)
        """
        values = RSI.extract_values(data, source)
        result = []
        
        # Calculate price changes
        deltas = np.diff(values)
        
        # Separate gains and losses
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Calculate initial average gain/loss
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        for i in range(len(values)):
            if i < period:
                result.append({
                    "time": RSI.get_time(data[i]),
                    "value": np.nan
                })
            elif i == period:
                # First RSI calculation
                if avg_loss == 0:
                    rsi_value = 100
                else:
                    rs = avg_gain / avg_loss
                    rsi_value = 100 - (100 / (1 + rs))
                
                result.append({
                    "time": RSI.get_time(data[i]),
                    "value": float(rsi_value)
                })
            else:
                # Smoothed average gain/loss
                current_gain = gains[i - 1]
                current_loss = losses[i - 1]
                
                avg_gain = (avg_gain * (period - 1) + current_gain) / period
                avg_loss = (avg_loss * (period - 1) + current_loss) / period
                
                if avg_loss == 0:
                    rsi_value = 100
                else:
                    rs = avg_gain / avg_loss
                    rsi_value = 100 - (100 / (1 + rs))
                
                result.append({
                    "time": RSI.get_time(data[i]),
                    "value": float(rsi_value)
                })
        
        return result


class MACD(IndicatorCalculator):
    """Moving Average Convergence Divergence"""
    
    @staticmethod
    def calculate(
        data: List[Dict[str, Any]],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        source: str = "close"
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Calculate MACD.
        
        Args:
            data: OHLC data
            fast_period: Fast EMA period (typically 12)
            slow_period: Slow EMA period (typically 26)
            signal_period: Signal line period (typically 9)
            source: Data source
        
        Returns:
            Tuple of (macd_line, signal_line, histogram)
        """
        values = MACD.extract_values(data, source)
        
        # Calculate fast and slow EMAs
        fast_ema = MovingAverage.ema(data, fast_period, source)
        slow_ema = MovingAverage.ema(data, slow_period, source)
        
        # Calculate MACD line (fast - slow)
        macd_line = []
        macd_values = []
        
        for i in range(len(data)):
            if not np.isnan(fast_ema[i]["value"]) and not np.isnan(slow_ema[i]["value"]):
                macd_val = fast_ema[i]["value"] - slow_ema[i]["value"]
                macd_values.append(macd_val)
            else:
                macd_val = np.nan
            
            macd_line.append({
                "time": MACD.get_time(data[i]),
                "value": float(macd_val) if not np.isnan(macd_val) else np.nan
            })
        
        # Calculate signal line (EMA of MACD)
        signal_line = []
        signal_ema = np.nan
        valid_macd = [v for v in macd_values if not np.isnan(v)]
        
        if len(valid_macd) >= signal_period:
            # Initialize with SMA
            signal_ema = np.mean(valid_macd[:signal_period])
            multiplier = 2 / (signal_period + 1)
        
        signal_idx = 0
        for i in range(len(data)):
            if np.isnan(macd_line[i]["value"]):
                signal_value = np.nan
            elif signal_idx < signal_period - 1:
                signal_value = np.nan
                signal_idx += 1
            elif signal_idx == signal_period - 1:
                signal_value = signal_ema
                signal_idx += 1
            else:
                # Calculate EMA
                signal_ema = (macd_line[i]["value"] - signal_ema) * multiplier + signal_ema
                signal_value = signal_ema
            
            signal_line.append({
                "time": MACD.get_time(data[i]),
                "value": float(signal_value) if not np.isnan(signal_value) else np.nan
            })
        
        # Calculate histogram (MACD - Signal)
        histogram = []
        for i in range(len(data)):
            if not np.isnan(macd_line[i]["value"]) and not np.isnan(signal_line[i]["value"]):
                hist_val = macd_line[i]["value"] - signal_line[i]["value"]
            else:
                hist_val = np.nan
            
            histogram.append({
                "time": MACD.get_time(data[i]),
                "value": float(hist_val) if not np.isnan(hist_val) else np.nan
            })
        
        return macd_line, signal_line, histogram


class BollingerBands(IndicatorCalculator):
    """Bollinger Bands"""
    
    @staticmethod
    def calculate(
        data: List[Dict[str, Any]],
        period: int = 20,
        std_dev: float = 2.0,
        source: str = "close"
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Calculate Bollinger Bands.
        
        Args:
            data: OHLC data
            period: Period for SMA (typically 20)
            std_dev: Standard deviation multiplier (typically 2)
            source: Data source
        
        Returns:
            Tuple of (upper_band, middle_band, lower_band)
        """
        values = BollingerBands.extract_values(data, source)
        
        upper_band = []
        middle_band = []
        lower_band = []
        
        for i in range(len(values)):
            if i < period - 1:
                upper_band.append({
                    "time": BollingerBands.get_time(data[i]),
                    "value": np.nan
                })
                middle_band.append({
                    "time": BollingerBands.get_time(data[i]),
                    "value": np.nan
                })
                lower_band.append({
                    "time": BollingerBands.get_time(data[i]),
                    "value": np.nan
                })
            else:
                # Calculate SMA (middle band)
                window = values[i - period + 1:i + 1]
                sma = np.mean(window)
                std = np.std(window)
                
                upper = sma + (std_dev * std)
                lower = sma - (std_dev * std)
                
                upper_band.append({
                    "time": BollingerBands.get_time(data[i]),
                    "value": float(upper)
                })
                middle_band.append({
                    "time": BollingerBands.get_time(data[i]),
                    "value": float(sma)
                })
                lower_band.append({
                    "time": BollingerBands.get_time(data[i]),
                    "value": float(lower)
                })
        
        return upper_band, middle_band, lower_band
