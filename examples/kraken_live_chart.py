"""
Kraken Live Chart - Real-time PAXG/USD with WebSocket
HYBRID: Uses OHLC + Trade feeds for real-time candle formation
"""

from lightweight_charts import Chart, CandleStickStyleOptions, HistogramStyleOptions
from datetime import datetime, timedelta
import asyncio
import websockets
import json
import logging
import threading
import time
import requests
from collections import deque
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KrakenLiveChart:
    """
    Real-time Kraken chart with HYBRID approach:
    - OHLC feed for completed candles
    - Trade feed for live updates to current forming candle
    """
    
    def __init__(self, pair: str = "PAXG/USD", interval: int = 5):
        self.pair = pair
        self.interval = interval  # Minutes
        self.ws_url = "wss://ws.kraken.com"
        self.ws = None
        
        # Data storage
        self.candles = deque(maxlen=200)
        self.current_candle = None
        self.current_candle_start_time = None
        
        # Chart components
        self.chart = None
        self.candle_series = None
        self.volume_series = None
        
        # Thread synchronization
        self.running = False
        
        logger.info(f"Kraken Live Chart: {pair} - {interval}m (HYBRID mode)")
    
    def fetch_historical_data(self, num_candles: int = 100):
        """Fetch historical OHLC data."""
        try:
            url = "https://api.kraken.com/0/public/OHLC"
            params = {
                "pair": self.pair.replace("/", ""),
                "interval": self.interval
            }
            
            logger.info(f"Fetching historical data...")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Failed: {response.status_code}")
                return
            
            data = response.json()
            
            if "error" in data and data["error"]:
                logger.error(f"API error: {data['error']}")
                return
            
            result = data.get("result", {})
            pair_keys = [k for k in result.keys() if k != "last"]
            
            if not pair_keys:
                logger.warning("No data received")
                return
            
            ohlc_data = result[pair_keys[0]]
            
            # Store all but the last candle (last might be forming)
            for ohlc in ohlc_data[-num_candles:-1]:
                timestamp = float(ohlc[0])
                
                candle = {
                    "time": datetime.fromtimestamp(timestamp),
                    "open": float(ohlc[1]),
                    "high": float(ohlc[2]),
                    "low": float(ohlc[3]),
                    "close": float(ohlc[4]),
                    "volume": float(ohlc[6])
                }
                
                self.candles.append(candle)
            
            # Initialize current candle from last OHLC
            if ohlc_data:
                last = ohlc_data[-1]
                timestamp = float(last[0])
                self.current_candle = {
                    "time": datetime.fromtimestamp(timestamp),
                    "open": float(last[1]),
                    "high": float(last[2]),
                    "low": float(last[3]),
                    "close": float(last[4]),
                    "volume": float(last[6])
                }
                self.current_candle_start_time = self.current_candle["time"]
                logger.info(f"Current forming candle initialized: {self.current_candle['time'].strftime('%H:%M')}")
            
            logger.info(f"✅ Loaded {len(self.candles)} completed + 1 forming candle")
            
        except Exception as e:
            logger.error(f"Error: {e}")
    
    def create_chart(self):
        """Create the chart."""
        self.chart = Chart(
            1400, 800,
            title=f"Kraken LIVE - {self.pair} ({self.interval}m) - Real-Time Formation",
            background_color="#0B0E11"
        )
        
        price_pane = self.chart.add_pane("Price", height_ratio=0.85)
        volume_pane = self.chart.add_pane("Volume", height_ratio=0.15)
        
        self.candle_series = price_pane.add_candlestick_series(
            self.pair,
            CandleStickStyleOptions(
                up_color="#26A69A",
                down_color="#EF5350",
                wick_color="#758696",
                border_visible=True,
                wick_visible=True
            )
        )
        
        self.volume_series = volume_pane.add_histogram_series(
            "Volume",
            HistogramStyleOptions(color="#5B9CF6", bar_width=0.8)
        )
        
        self.chart.set_crosshair_colors(vert_color="#758696", horiz_color="#758696")
        
        logger.info("✅ Chart created")
    
    def _get_candle_start_time(self, trade_time: datetime) -> datetime:
        """Get the start time of the candle period for a given trade time."""
        minutes = (trade_time.minute // self.interval) * self.interval
        return trade_time.replace(minute=minutes, second=0, microsecond=0)
    
    async def connect(self):
        """Connect to Kraken WebSocket."""
        try:
            self.ws = await websockets.connect(self.ws_url)
            logger.info("✅ Connected to Kraken")
            
            # Subscribe to trade feed first
            trade_sub = {
                "event": "subscribe",
                "pair": [self.pair],
                "subscription": {"name": "trade"}
            }
            await self.ws.send(json.dumps(trade_sub))
            logger.info(f"📊 Subscribed to {self.pair} TRADE feed")
            
            # Small delay
            await asyncio.sleep(0.1)
            
            # Subscribe to OHLC feed
            ohlc_sub = {
                "event": "subscribe",
                "pair": [self.pair],
                "subscription": {"name": "ohlc", "interval": self.interval}
            }
            await self.ws.send(json.dumps(ohlc_sub))
            logger.info(f"📊 Subscribed to {self.pair} OHLC {self.interval}m")
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise
    
    async def listen(self):
        """Listen for WebSocket messages."""
        if not self.ws:
            logger.error("WebSocket not connected")
            return
            
        self.running = True
        
        try:
            async for message in self.ws:  # type: ignore[union-attr]
                if not self.running:
                    break
                
                data = json.loads(message)
                
                if isinstance(data, dict):
                    event = data.get("event")
                    if event in ["heartbeat", "systemStatus"]:
                        continue
                    elif event == "subscriptionStatus":
                        logger.info(f"Subscription: {data.get('status')} - {data.get('channelName')}")
                        continue
                
                if isinstance(data, list) and len(data) >= 4:
                    channel_name = data[2] if len(data) > 2 else ""
                    
                    if "trade" in channel_name.lower():
                        await self._process_trade(data)
                    elif "ohlc" in channel_name.lower():
                        await self._process_ohlc(data)
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket closed")
        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.running = False
    
    async def _process_trade(self, data: list):
        """
        Process trade data to update current forming candle in REAL-TIME.
        Format: [channelID, [[price, volume, time, side, orderType, misc]], channelName, pair]
        """
        try:
            trades = data[1]
            
            for trade in trades:
                price = float(trade[0])
                volume = float(trade[1])
                trade_timestamp = float(trade[2])
                
                trade_time = datetime.fromtimestamp(trade_timestamp)
                candle_start = self._get_candle_start_time(trade_time)
                
                # Initialize current candle if needed
                if self.current_candle is None:
                    self.current_candle = {
                        "time": candle_start,
                        "open": price,
                        "high": price,
                        "low": price,
                        "close": price,
                        "volume": volume
                    }
                    self.current_candle_start_time = candle_start
                    print(f"✨ Started tracking candle at {candle_start.strftime('%H:%M')}")
                    continue
                
                # Check if trade belongs to current candle
                if candle_start == self.current_candle_start_time:
                    # Update current candle with trade
                    old_close = self.current_candle["close"]
                    self.current_candle["high"] = max(self.current_candle["high"], price)
                    self.current_candle["low"] = min(self.current_candle["low"], price)
                    self.current_candle["close"] = price
                    self.current_candle["volume"] += volume
                    
                    print(f"💹 TRADE UPDATE: {price:.2f} (Close {old_close:.2f}→{price:.2f}, Vol +{volume:.4f})")
                else:
                    # New candle period - save old one
                    print(f"\\n🕯️ Candle completed: {self.current_candle['time'].strftime('%H:%M')}")
                    self.candles.append(self.current_candle)
                    
                    # Start new candle
                    self.current_candle = {
                        "time": candle_start,
                        "open": price,
                        "high": price,
                        "low": price,
                        "close": price,
                        "volume": volume
                    }
                    self.current_candle_start_time = candle_start
                    print(f"✨ NEW candle started at {candle_start.strftime('%H:%M')}: O:{price:.2f}\\n")
            
        except Exception as e:
            logger.error(f"Trade processing error: {e}")
    
    async def _process_ohlc(self, data: list):
        """Process OHLC data for candle completion confirmation."""
        try:
            ohlc_data = data[1]
            if len(ohlc_data) < 8:
                return
            
            timestamp = float(ohlc_data[0])
            candle_time = datetime.fromtimestamp(timestamp)
            
            # OHLC messages confirm candle completion
            # We already handle this with trades, but this serves as backup
            print(f"📊 OHLC confirmation for {candle_time.strftime('%H:%M')}")
            
        except Exception as e:
            logger.error(f"OHLC error: {e}")
    
    def update_chart(self):
        """Update chart with current candle - TradingView style."""
        if not self.chart or not self.candle_series or not self.current_candle:
            return
        
        try:
            # Update candle series with current bar (TradingView approach)
            self.candle_series.update(self.current_candle)  # type: ignore[union-attr]
            
            # Update volume series
            volume_bar = {"time": self.current_candle["time"], "value": self.current_candle["volume"]}
            self.volume_series.update(volume_bar)  # type: ignore[union-attr]
            
            # Update time scale with all data
            all_candles = list(self.candles) + [self.current_candle]
            self.chart.update_time_scale_data(all_candles)
            
            # Force visual update for each pane
            for pane in self.chart.panes:
                pane.update_price_scale()
                pane.update_visuals()
            
            # Force canvas redraw
            self.chart.canvas.update()
            
        except Exception as e:
            logger.error(f"Chart update error: {e}")
    
    async def disconnect(self):
        """Disconnect."""
        self.running = False
        if self.ws:
            await self.ws.close()


def run_websocket(live_chart):
    """Run WebSocket in thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def ws_main():
        try:
            await live_chart.connect()
            await live_chart.listen()
        except Exception as e:
            logger.error(f"WS error: {e}")
    
    loop.run_until_complete(ws_main())


def main():
    """Main function."""
    print("🚀 Kraken LIVE Chart - HYBRID MODE")
    print("📊 PAXG/USD - 5 minute candles")
    print("💹 Real-time candle formation with trade feed!")
    print("=" * 50)
    
    live_chart = KrakenLiveChart(pair="PAXG/USD", interval=5)
    
    print("📥 Fetching historical data...")
    live_chart.fetch_historical_data(num_candles=100)
    
    live_chart.create_chart()
    
    # Initial display
    if live_chart.candles or live_chart.current_candle:
        all_candles = list(live_chart.candles)
        if live_chart.current_candle:
            all_candles.append(live_chart.current_candle)
        
        live_chart.candle_series.set_data(all_candles)  # type: ignore[union-attr]
        volume_data = [{"time": c["time"], "value": c["volume"]} for c in all_candles]
        live_chart.volume_series.set_data(volume_data)  # type: ignore[union-attr]
        live_chart.chart.update_time_scale_data(all_candles)  # type: ignore[union-attr]
        
        # Force initial render
        for pane in live_chart.chart.panes:  # type: ignore[union-attr]
            pane.update_price_scale()
            pane.update_visuals()
        
        print(f"✅ Displaying {len(all_candles)} candles (including forming candle)")
    
    # Start WebSocket
    ws_thread = threading.Thread(target=run_websocket, args=(live_chart,), daemon=True)
    ws_thread.start()
    
    print("✅ WebSocket started - Trade feed active!")
    
    # Chart updates at 10 FPS
    from vispy import app
    
    def update_timer(event):
        live_chart.update_chart()
    
    timer = app.Timer(interval=0.1, connect=update_timer, start=True)
    
    print("✅ Chart ready!")
    print("\\n💡 Watch the LAST candle update in real-time as trades occur!")
    print("📈 High/Low/Close will change with every trade")
    print("🛑 Close window to exit\\n")
    
    if live_chart.chart:
        live_chart.chart.render()  # type: ignore[union-attr]


if __name__ == "__main__":
    main()
