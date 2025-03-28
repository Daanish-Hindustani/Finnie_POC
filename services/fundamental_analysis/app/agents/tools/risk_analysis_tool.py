from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import yfinance as yf
import numpy as np
import pandas as pd

class RiskCallToolInput(BaseModel):
    """Input schema for EarningsCallTool."""
    stock_symbol: str = Field(..., description="Stock ticker symbol (e.g., AAPL, TSLA).")


class Risk(BaseModel):
    ticker: str
    volatility: float
    beta: float
    


class RiskTool(BaseTool):
    name: str = "Risk Analysis Tool"
    description: str = "Fetches detailed metrics for assessing stock risk, such as volatility and beta."
    args_schema: Type[BaseModel] = RiskCallToolInput

    def _run(self, stock_symbol: str) -> dict:
        stock_data = self.fetch_stock_data(stock_symbol)
        market_data = self.fetch_market_data()

        volatility = self.calculate_volatility(stock_data)
        beta = self.calculate_beta(stock_data, market_data)

        result = Risk(ticker=stock_symbol, volatility=volatility, beta=beta)
        return result

    def fetch_stock_data(self, stock_symbol: str) -> pd.DataFrame:
        """Fetch historical stock data."""
        stock_data = yf.download(stock_symbol, period="1y", interval="1d")
        stock_data['Daily Return'] = stock_data['Close'].pct_change()
        return stock_data

    def fetch_market_data(self) -> pd.DataFrame:
        """Fetch market data (S&P 500 as the benchmark)."""
        market_data = yf.download('^GSPC', period="1y", interval="1d")
        market_data['Daily Return'] = market_data['Close'].pct_change()
        return market_data

    def calculate_volatility(self, stock_data: pd.DataFrame) -> float:
        """Calculate the annualized volatility of the stock."""
        volatility = stock_data['Daily Return'].std() * np.sqrt(252)  
        return volatility

    def calculate_beta(self, stock_data: pd.DataFrame, market_data: pd.DataFrame) -> float:
        """Calculate the stock's beta against the market (S&P 500)."""
        covariance = np.cov(stock_data['Daily Return'].dropna(), market_data['Daily Return'].dropna())[0][1]
        market_variance = market_data['Daily Return'].var()
        beta = covariance / market_variance
        return beta


