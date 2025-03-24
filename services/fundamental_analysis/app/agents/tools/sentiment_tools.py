from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, List
import yfinance as yf
from textblob import TextBlob


class SentimentToolInput(BaseModel):
    """Input schema for SentimentTool."""
    stock_symbol: str = Field(..., description="Stock ticker symbol (e.g., AAPL, TSLA).")


class Info(BaseModel):
    id: str
    sentiment_score: float
    context: List[str]


class SentimentToolOutput(BaseModel):
    main_stock_info: Info
    sector_stock_info: Info
    industry_stock_info: Info


class SentimentTool(BaseTool):
    name: str = "Sentiment Analysis Tool"
    description: str = (
        "Analyzes the sentiment of a stock, its sector, and industry by gathering news articles and computing sentiment scores."
    )
    args_schema: Type[BaseModel] = SentimentToolInput

    def _run(self, stock_symbol: str) -> SentimentToolOutput:
        try:
            main_stock_news = self.get_context_stock(stock_symbol)
            main_stock_sentiment = self.get_sentiment_score(main_stock_news)
            main_stock_info = Info(id=stock_symbol, sentiment_score=main_stock_sentiment, context=main_stock_news)

            # Fetch industry and sector information
            stock_info = yf.Ticker(stock_symbol).info
            industry = stock_info.get('industry', 'Unknown Industry')
            sector = stock_info.get('sector', 'Unknown Sector')

            # Industry sentiment
            industry_context = self.get_context_industry(industry)
            industry_sentiment = self.get_sentiment_score(industry_context)
            industry_info = Info(id=industry, sentiment_score=industry_sentiment, context=industry_context)

            # Sector sentiment
            sector_context = self.get_context_sector(sector)
            sector_sentiment = self.get_sentiment_score(sector_context)
            sector_info = Info(id=sector, sentiment_score=sector_sentiment, context=sector_context)

            return dict(SentimentToolOutput(
                main_stock_info=main_stock_info,
                sector_stock_info=sector_info,
                industry_stock_info=industry_info,
            ))
        except Exception as e:
            print(f"Error in running SentimentTool: {e}")
            return SentimentToolOutput(
                main_stock_info=Info(id=stock_symbol, sentiment_score=0.0, context=[]),
                sector_stock_info=Info(id="Unknown", sentiment_score=0.0, context=[]),
                industry_stock_info=Info(id="Unknown", sentiment_score=0.0, context=[]),
            )

    def get_sentiment_score(self, news: List[str]) -> float:
        try:
            if not news:
                return 0.0
            return sum(TextBlob(content).sentiment.polarity for content in news) / len(news)
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return 0.0

    def get_context_stock(self, stock_symbol: str) -> List[str]:
        try:
            stock = yf.Ticker(stock_symbol)
            news = stock.get_news()
            return [item["content"].get("summary", "") for item in news[:5]] if news else []
        except Exception as e:
            print(f"Error fetching stock news: {e}")
            return []

    def get_context_industry(self, industry: str) -> List[str]:
        return self.get_industry_reports(industry)

    def get_context_sector(self, sector: str) -> List[str]:
        return self.get_sector_reports(sector)

    def get_industry_reports(self, industry: str) -> List[str]:
        try:
            formatted_industry = self.format_category(industry)
            reports = yf.Industry(formatted_industry).research_reports
            return [report.get('reportTitle', "") for report in reports] if reports else []
        except Exception as e:
            print(f"Error fetching industry reports for {industry}: {e}")
            return []

    def get_sector_reports(self, sector: str) -> List[str]:
        try:
            formatted_sector = self.format_category(sector)
            reports = yf.Sector(formatted_sector).research_reports
            return [report.get('reportTitle', "") for report in reports] if reports else []
        except Exception as e:
            print(f"Error fetching sector reports for {sector}: {e}")
            return []

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

