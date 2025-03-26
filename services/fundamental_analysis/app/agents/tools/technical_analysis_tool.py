from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import yfinance as yf
import numpy as np
import pandas as pd

class TechnicalAnalysisCallToolInput(BaseModel):
    """Input schema for TechnicalAnalysis tool."""
    stock_symbol: str = Field(..., description="Stock ticker symbol (e.g., AAPL, TSLA).")


class TechnicalAnalysisOutput(BaseModel):
    """Output schema for TechnicalAnalysis tool."""
    historical_performance: float
    beta: float
    moving_averages: dict
    rsi: float
    bollinger_bands: dict

class TechnicalAnalysis(BaseTool):
    name: str = "Technical Analysis Tool"
    description: str = "Fetches detailed metrics for assessing stock risk and long-term investment potential, such as historical performance, beta, long-term moving averages, RSI, and Bollinger Bands."
    args_schema: Type[BaseModel] = TechnicalAnalysisCallToolInput

    def _run(self, stock_symbol: str) -> TechnicalAnalysisOutput:
        stock = yf.Ticker(stock_symbol)
        data = stock.history(period="10y")
        if data.empty:
            return {"error": "Invalid stock symbol or no data available."}
        
        return TechnicalAnalysisOutput(
            historical_performance=self.calculate_historical_performance(data),
            beta=self.calculate_beta(stock_symbol),
            moving_averages=self.calculate_long_term_moving_averages(data),
            rsi=self.calculate_rsi(data),
            bollinger_bands=self.calculate_bollinger_bands(data)
        )
    
    def calculate_historical_performance(self, data):
        start_price = data['Close'].iloc[0]
        end_price = data['Close'].iloc[-1]
        annual_return = ((end_price / start_price) ** (1 / 10)) - 1
        return round(annual_return * 100, 2)

    def calculate_beta(self, stock_symbol):
        market = yf.Ticker("^GSPC").history(period="10y")
        stock = yf.Ticker(stock_symbol).history(period="10y")
        if market.empty or stock.empty:
            return None
        
        market_returns = market['Close'].pct_change().dropna()
        stock_returns = stock['Close'].pct_change().dropna()
        
        cov_matrix = np.cov(stock_returns, market_returns)
        beta = cov_matrix[0, 1] / cov_matrix[1, 1]
        return round(beta, 4)
    
    def calculate_long_term_moving_averages(self, data):
        return {
            "200-day": round(data['Close'].rolling(window=200).mean().iloc[-1], 2),
            "500-day": round(data['Close'].rolling(window=500).mean().iloc[-1], 2),
            "1000-day": round(data['Close'].rolling(window=1000).mean().iloc[-1], 2)
        }

    def calculate_rsi(self, data, period=14):
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi.iloc[-1], 2)
    
    def calculate_bollinger_bands(self, data, window=200):
        rolling_mean = data['Close'].rolling(window=window).mean()
        rolling_std = data['Close'].rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * 2)
        lower_band = rolling_mean - (rolling_std * 2)
        return {
            "upper_band": round(upper_band.iloc[-1], 2),
            "lower_band": round(lower_band.iloc[-1], 2)
        }

print(TechnicalAnalysis()._run("GOOGL"))