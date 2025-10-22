"""
Kraken WebSocket Real-Time Data Example
Connects to Kraken WebSocket API for live PAXG/USD data with 5-minute candles
"""

from lightweight_charts import Chart, CandleStickStyleOptions, HistogramStyleOptions
from datetime import datetime, timedelta
import asyncio
import websockets
import json
import logging
from collections import defaultdict
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KrakenWebSocket:
    """
    Kraken WebSocket client for real-time OHLC and trade data.
    """
    
    def __init__(self, pair: str = "PAXG/USD", interval: int = 5):
        """
        Initialize Kraken WebSocket client.
        
        Args:
            pair: Trading pair (e.g., "PAXG/USD")
            interval: Candle interval in minutes (1, 5, 15, 30, 60, etc.)
        """
        self.pair = pair
        self.interval = interval
        self.ws_url = "wss://ws.kraken.com"
        self.ws = None
        
        # Convert pair format for Kraken (PAXG/USD -> XAU/USD in Kraken format)
        self.kraken_pair = self._convert_pair_format(pair)
        
        # Store candle data
        self.candles: List[Dict] = []
        self.current_candle: Optional[Dict] = None
        self.volumes: Dict[datetime, float] = {}
        
        # Callbacks
        self.on_candle_update: Optional[callable] = None  # type: ignore[valid-type]
        self.on_new_candle: Optional[callable] = None  # type: ignore[valid-type]
        
        logger.info(f"Kraken WebSocket initialized for {pair} ({self.kraken_pair}) - {interval}m candles")
    
    def _convert_pair_format(self, pair: str) -> str:
        """
        Convert pair to Kraken WebSocket format.
        Kraken REST API uses different names than WebSocket.
        WebSocket typically uses the base format without X prefix.
        """
        # Kraken WebSocket pair formats
        # Note: PAXG is listed as "PAXGUSD" in WebSocket
        conversions = {
            "PAXG/USD": "PAXG/USD",
            "BTC/USD": "XBT/USD",  # Bitcoin uses XBT on Kraken
            "ETH/USD": "ETH/USD",
            "XRP/USD": "XRP/USD"
        }
        result = conversions.get(pair, pair)
        logger.info(f"Pair conversion: {pair} -> {result}")
        return result
    
    async def connect(self):
        """Connect to Kraken WebSocket."""
        try:
            self.ws = await websockets.connect(self.ws_url)
            logger.info(f"✅ Connected to Kraken WebSocket")
            
            # Subscribe to OHLC (candles) data
            subscribe_message = {
                "event": "subscribe",
                "pair": [self.kraken_pair],
                "subscription": {
                    "name": "ohlc",
                    "interval": self.interval
                }
            }
            
            await self.ws.send(json.dumps(subscribe_message))
            logger.info(f"📊 Subscribed to OHLC {self.interval}m for {self.kraken_pair}")
            
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            raise
    
    async def listen(self):
        """Listen for WebSocket messages."""
        if not self.ws:
            logger.error("WebSocket not connected")
            return
            
        try:
            async for message in self.ws:  # type: ignore[union-attr]
                data = json.loads(message)
                
                # Skip heartbeat and system messages
                if isinstance(data, dict):
                    event = data.get("event")
                    if event == "heartbeat":
                        continue
                    elif event == "systemStatus":
                        logger.info(f"System status: {data.get('status')}")
                        continue
                    elif event == "subscriptionStatus":
                        status = data.get('status')
                        if status == "error":
                            logger.error(f"❌ Subscription error: {data}")
                        else:
                            logger.info(f"Subscription: {status} - {data.get('channelName')}")
                        continue
                
                # Process OHLC data
                if isinstance(data, list) and len(data) >= 4:
                    await self._process_ohlc(data)
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("⚠️ WebSocket connection closed")
        except Exception as e:
            logger.error(f"❌ Error in listen loop: {e}")
    
    async def _process_ohlc(self, data: list):
        """
        Process OHLC data from Kraken.
        
        Format: [channelID, [time, etime, open, high, low, close, vwap, volume, count], channelName, pair]
        """
        try:
            if len(data) < 4:
                return
            
            ohlc_data = data[1]
            if len(ohlc_data) < 8:
                return
            
            # Parse OHLC data
            timestamp = float(ohlc_data[0])
            end_time = float(ohlc_data[1])
            open_price = float(ohlc_data[2])
            high_price = float(ohlc_data[3])
            low_price = float(ohlc_data[4])
            close_price = float(ohlc_data[5])
            volume = float(ohlc_data[7])
            
            # Convert timestamp to datetime
            dt = datetime.fromtimestamp(timestamp)
            
            # Create candle dict
            candle = {
                "time": dt,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": volume
            }
            
            # Check if this is an update to current candle or a new candle
            if self.current_candle and self.current_candle["time"] == dt:
                # Update current candle
                self.current_candle = candle
                if self.on_candle_update:
                    self.on_candle_update(candle)
            else:
                # New candle
                if self.current_candle:
                    # Finalize previous candle
                    self.candles.append(self.current_candle)
                    if self.on_new_candle:
                        self.on_new_candle(self.current_candle)
                
                self.current_candle = candle
                logger.info(f"🕯️ New {self.interval}m candle: {dt} | O:{open_price:.2f} H:{high_price:.2f} L:{low_price:.2f} C:{close_price:.2f} V:{volume:.2f}")
            
        except Exception as e:
            logger.error(f"Error processing OHLC: {e}")
    
    async def disconnect(self):
        """Disconnect from WebSocket."""
        if self.ws:
            await self.ws.close()
            logger.info("Disconnected from Kraken WebSocket")
    
    def get_candles(self) -> List[Dict]:
        """Get all completed candles."""
        return self.candles.copy()
    
    def get_current_candle(self) -> Optional[Dict]:
        """Get the current (incomplete) candle."""
        return self.current_candle


async def main():
    """Main function to run real-time chart with Kraken data."""
    
    # Initialize Kraken WebSocket
    kraken = KrakenWebSocket(pair="PAXG/USD", interval=5)
    
    # Store initial historical data (you'd normally fetch this from Kraken REST API)
    # For now, we'll start with empty and let it populate
    historical_data = []
    
    print("🚀 Starting Kraken WebSocket Real-Time Chart")
    print(f"📊 Pair: PAXG/USD")
    print(f"⏱️  Interval: 5 minutes")
    print(f"🔗 Connecting to Kraken...")
    
    # Connect to Kraken
    await kraken.connect()
    
    # Set up callbacks for chart updates
    def on_candle_update(candle):
        """Called when current candle updates."""
        logger.info(f"📈 Candle update: C:{candle['close']:.2f}")
        # In a real implementation, you'd update the chart here
    
    def on_new_candle(candle):
        """Called when a new candle starts."""
        logger.info(f"✨ New candle completed!")
        # In a real implementation, you'd add the candle to the chart
    
    kraken.on_candle_update = on_candle_update
    kraken.on_new_candle = on_new_candle
    
    # Listen for updates
    print("✅ Connected! Listening for real-time data...")
    print("Press Ctrl+C to stop\n")
    
    try:
        await kraken.listen()
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
    finally:
        await kraken.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
