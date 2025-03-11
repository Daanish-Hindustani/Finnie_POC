from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, List
import yfinance as yf
from ollama import chat

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

    def _run(self, stock_symbol: str) -> dict:
        info = yf.Ticker(stock_symbol).info
        sector = info.get('sector')
        industry = info.get('industry')

        main_stock_info = self.getStockInfo(stock_symbol)
        competitors = self.getCompetitors(industry, sector, stock_symbol)

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

    def getCompetitors(self, industry: str, sector: str, stock_symbol: str) -> List[Competitor]:
        response = chat(
            messages=[
                {
                    'role': 'user',
                    'content': f'Given the industry:{industry} and sector:{sector} find 3 competitors of {stock_symbol}, Note: FB ticker is now META and TWT is now X',
                }
            ],
            model='gemma2:2b',
            format=Competitor.model_json_schema(),  # Pass schema for structured output
        )

        # Validate and parse the response into a Pydantic model
        competitors = Competitor.model_validate_json(response.message.content)

        # Convert the Pydantic model into a dictionary
        competitors = competitors.model_dump()
        
        return competitors["tickers"]


# Example usage:
c = CompetitorTool()
print(c._run("GOOGL"))
