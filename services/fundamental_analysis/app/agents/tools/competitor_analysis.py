from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, List
import yfinance as yf
from ollama import chat
import pandas as pd

class CompetitorToolInput(BaseModel):
    """Input schema for StockCompetitorAnalysisTool."""
    stock_symbol: str = Field(..., description="Stock ticker symbol (e.g., AAPL, TSLA).")

class StockInfo(BaseModel):
    ticker: str
    marketCap: str
    net_profit_margin: str
    return_on_equity: str
    sales_per_share: str
    long_term_debt_to_equity: str
    eps_5year_forecast: str

class Competitor(BaseModel):
    tickers: List[str]


class CompetitorTool(BaseTool):
    name: str = "Stock Competitor Analysis Tool"
    description: str = "Analyzes a stock's sector and industry, finds competitors, and computes sector/industry averages."
    args_schema: Type[BaseModel] = CompetitorToolInput
    
    def _run(self, stock_symbol) -> dict:
        info = yf.Ticker(stock_symbol).info
        sector = info.get('sector')
        industry = info.get('industry')

        main_stock_info = self.getStockInfo(stock_symbol)
        competitors = self.getCompetitors(industry, sector)

        results = {
            "main_stock": main_stock_info.model_dump(),
            "competitors": [self.getStockInfo(c).model_dump() for c in competitors]
        }

        return results

    def getStockInfo(self, stock_symbol) -> StockInfo:
        stock = yf.Ticker(stock_symbol)
        info = stock.info

        return StockInfo(
            ticker=stock_symbol,
            marketCap=str(info.get("marketCap", "N/A")),
            net_profit_margin=str(info.get("profitMargins", "N/A")),
            return_on_equity=str(info.get("returnOnEquity", "N/A")),
            sales_per_share=str(info.get("revenuePerShare", "N/A")),
            long_term_debt_to_equity=str(info.get("debtToEquity", "N/A")),
            eps_5year_forecast=str(info.get("earningsGrowth", "N/A")),
        )

    def getCompetitors(self, industry: str, sector: str) -> List[Competitor]:
        
        industry_competitors = pd.DataFrame(yf.Industry(self.format_category(industry)).top_companies)
        sector_competitors = yf.Sector(self.format_category(sector)).top_companies
        industry_competitors = [key for key in industry_competitors['name'].to_dict().keys()]
        sector_competitors = [key for key in sector_competitors['name'].to_dict().keys()]
        
        competitors = list(set(industry_competitors) | set(sector_competitors))

        return Competitor(tickers=competitors)
    
    def format_category(self, text: str) -> str:
        if "-" not in text:
            try:
                res = []
                for word in text.split():
                    if word != "-" and word != "&":
                        res.append(word.lower())
                return "-".join(res)
            except Exception as e:
                print(f"Error formatting category: {e}")
                return "unknown"
        return text
