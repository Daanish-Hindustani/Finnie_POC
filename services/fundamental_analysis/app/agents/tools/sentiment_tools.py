from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, List
import yfinance as yf
from ollama import chat
from textblob import TextBlob
import requests
from bs4 import BeautifulSoup


class SentimentToolInput(BaseModel):
    """Input schema for SentimentTool."""
    stock_symbol: str = Field(..., description="Stock ticker symbol (e.g., AAPL, TSLA).")


class Info(BaseModel):
    id: str
    sentiment_score: float
    context: List[str]


class Competitor(BaseModel):
    tickers: List[str]


class SentimentToolOutput(BaseModel):
    main_stock_info: Info
    sector_stock_info: Info
    industry_stock_info: Info


class IndustrySectorResponse(BaseModel):
    sector: str = Field(...)
    industry: str = Field(...)


class NewScrapperLLMResponse(BaseModel):
    news: List[str]


class SentimentTool(BaseTool):
    name: str = "Sentiment Analysis Tool"
    description: str = "Analyzes the sentiment a stock's sector and industry and the stock itself, finds news articles and calculates the sentiment."
    args_schema: Type[BaseModel] = SentimentToolInput

    def _run(self, stock_symbol: str) -> SentimentToolOutput:
        main_stock_news = self.getContextStock(stock_symbol)
        main_stock_sentiment = self.getSentimentScore(main_stock_news)
        main_stock_info = Info(id=stock_symbol, sentiment_score=main_stock_sentiment, context=main_stock_news)

        # Get Industry and Sector
        info = self.getIndustrySector(stock_symbol)
        sector, industry = info

        industry_news = self.getContextIndustry(industry)
        industry_sentiment = self.getSentimentScore(industry_news)
        industry_info = Info(id=industry, sentiment_score=industry_sentiment, context=industry_news)

        sector_news = self.getContextSector(sector)
        sector_sentiment = self.getSentimentScore(sector_news)
        sector_info = Info(id=sector, sentiment_score=sector_sentiment, context=sector_news)

        return SentimentToolOutput(
            main_stock_info=main_stock_info,
            sector_stock_info=sector_info,
            industry_stock_info=industry_info
        )

    def getSentimentScore(self, news: List[str]) -> float:
        if not news:
            return 0.0
        score = sum(TextBlob(title).sentiment.polarity for title in news)
        return score / len(news)

    # Todo: add summary inplace of title
    def getContextStock(self, stock_symbol: str) -> List[str]:
        stock = yf.Ticker(stock_symbol)
        if not stock.news:
            return []
        return [item["content"]["title"] for item in stock.news[:5]]

    def getContextIndustry(self, industry: str) -> List[str]:
        response = chat(
            messages=[{
                'role': 'user',
                'content': f'Find the top 5 most relevant news titles for the industry: {industry} today.',
            }],
            model='gemma2:2b',
            format=NewScrapperLLMResponse.model_json_schema()
        )

        try:
            news_response = NewScrapperLLMResponse.model_validate_json(response.message.content)
            return news_response.news
        except Exception as e:
            return [f"Error parsing LLM response: {str(e)}"]

    def getContextSector(self, sector: str) -> List[str]:
        response = chat(
            messages=[{
                'role': 'user',
                'content': f'Find the top 5 most relevant news titles for the sector: {sector} today.',
            }],
            model='gemma2:2b',
            format=NewScrapperLLMResponse.model_json_schema()
        )

        try:
            news_response = NewScrapperLLMResponse.model_validate_json(response.message.content)
            return news_response.news
        except Exception as e:
            return [f"Error parsing LLM response: {str(e)}"]

    def getIndustrySector(self, stock_symbol: str) -> List[str]:
        response = chat(
            messages=[{
                'role': 'user',
                'content': f'Retrieve the industry and sector for the stock: {stock_symbol}.',
            }],
            model='gemma2:2b',
            format=IndustrySectorResponse.model_json_schema()
        )

        try:
            info = IndustrySectorResponse.model_validate_json(response.message.content)
            return [info.sector, info.industry]
        except Exception as e:
            return [f"Error retrieving sector: {str(e)}", "Unknown"]


tool = SentimentTool()

print(tool._run(stock_symbol = "GOOGL"))