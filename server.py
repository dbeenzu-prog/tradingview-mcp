import os
from mcp.server.fastmcp import FastMCP
from tvDatafeed import TvDatafeed, Interval
from tradingview_ta import TA_Handler, Interval as TAInterval

mcp = FastMCP("TradingView Price Action")
tv = TvDatafeed()

INTERVAL_MAP = {
    "1m": Interval.in_1_minute,
    "5m": Interval.in_5_minute,
    "15m": Interval.in_15_minute,
    "1h": Interval.in_1_hour,
    "4h": Interval.in_4_hour,
    "1d": Interval.in_daily,
}

@mcp.tool()
def get_candles(symbol: str = "EURUSD", exchange: str = "OANDA", timeframe: str = "1h", bars: int = 50) -> str:
    """Fetch raw OHLCV candle data from TradingView for price action analysis."""
    interval = INTERVAL_MAP.get(timeframe.lower(), Interval.in_1_hour)
    df = tv.get_hist(symbol=symbol.upper(), exchange=exchange.upper(), interval=interval, n_bars=bars)
    if df is None or df.empty:
        return f"No data returned for {exchange}:{symbol} on {timeframe}."
    return df[["open", "high", "low", "close", "volume"]].tail(bars).to_string()

@mcp.tool()
def get_ta_summary(symbol: str = "EURUSD", exchange: str = "OANDA", screener: str = "forex", interval: str = "1h") -> str:
    """Get TradingView oscillator and moving average summary."""
    handler = TA_Handler(
        symbol=symbol.upper(),
        screener=screener.lower(),
        exchange=exchange.upper(),
        interval=interval.lower()
    )
    analysis = handler.get_analysis()
    return str({
        "summary": analysis.summary,
        "oscillators": analysis.oscillators,
        "moving_averages": analysis.moving_averages
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    mcp.run(transport="sse", host="0.0.0.0", port=port)
