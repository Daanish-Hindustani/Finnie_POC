from crewai import Agent, Task, Crew, LLM
# from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
from tools import competitor_analysis, earnings_report_tool, risk_analysis_tool, sentiment_tools, technical_analysis_tool
load_dotenv()

def create_crew(stock_symbol):
    llm = LLM(
        model="ollama/gemma2:2b",
        base_url="http://localhost:11434"
    )
    
    # Agents
    
    # Analyst
    analyst = Agent(
        role="Financial Analyst",
        goal="Interpret gathered stock data to provide actionable investment insights and recommendations.",
        backstory="You're a seasoned financial analyst known for making accurate market predictions by synthesizing complex financial data, intrinsic value, industry trends, and company fundamentals.",
        tools=[competitor_analysis.CompetitorTool(), earnings_report_tool.EarningsCallTool(), risk_analysis_tool.RiskTool()],
        llm=llm
    )

    # Sentiment
    sentiment = Agent(
        role="Market Sentiment Analyst",
        goal="Analyze news articles, social media, and earnings call transcripts to gauge market sentiment on a stock.",
        backstory="You're an expert in financial sentiment analysis, skilled in identifying bullish and bearish trends from news, social media, and investor sentiment.",
        tools=[SerperDevTool(), sentiment_tools.SentimentTool()],
        llm=llm
    )

    # Risk Assessor
    risk_assessor = Agent(
        role="Risk Assessment Specialist",
        goal="Evaluate the risks associated with a stock, including volatility, financial stability, and market conditions.",
        backstory="You're a highly skilled risk analyst with expertise in identifying financial, macroeconomic, and market risks that could impact investment decisions.",
        tools=[risk_analysis_tool.RiskTool()],
        llm=llm
    )

    # Insider Trading Analyst
    insider_trading_analyst = Agent(
        role="Insider & Institutional Trading Analyst",
        goal="Analyze insider transactions and institutional investments to assess market confidence in a stock.",
        backstory="You're a market expert skilled in tracking insider trades and institutional investments to gauge investor confidence.",
        tools=[SerperDevTool()],
        llm=llm
    )

    # Macroeconomic & Industry Analyst
    macro_industry_analyst = Agent(
        role="Macroeconomic & Industry Analyst",
        goal="Assess macroeconomic factors and industry trends that influence stock performance.",
        backstory="You're a macroeconomic strategist with expertise in economic indicators, sector performance, and global market trends.",
        tools=[SerperDevTool()],
        llm=llm
    )

    # Technical Analyst
    technical_analyst = Agent(
        role="Technical Analyst",
        goal="Analyze stock price movements, chart patterns, and indicators to identify trading opportunities.",
        backstory="You're a technical analysis expert skilled in identifying market trends using chart patterns, indicators, and historical price data.",
        tools=[technical_analysis_tool.TechnicalAnalysis()],
        llm=llm
    )

    # Tasks

    # Analyst Task
    analyst_task = Task(
        description="Synthesize financial data, industry trends, and valuation metrics to provide a comprehensive investment recommendation for the stock.",
        expected_output="A detailed investment report with insights on stock valuation, growth potential, and potential risks.",
        agent=analyst
    )

    # Sentiment Analysis Task
    sentiment_task = Task(
        description="Gather and analyze news articles, social media discussions, and earnings call transcripts to determine the market sentiment for the stock.",
        expected_output="A sentiment report categorizing the market outlook as bullish, bearish, or neutral with supporting evidence.",
        agent=sentiment
    )

    # Risk Assessment Task
    risk_task = Task(
        description="Evaluate the financial, market, and macroeconomic risks associated with investing in the stock, including volatility and liquidity risks.",
        expected_output="A risk assessment report detailing factors such as volatility, debt levels, and macroeconomic concerns.",
        agent=risk_assessor
    )

    # Insider Trading & Institutional Holdings Task
    insider_trading_task = Task(
        description="Analyze insider transactions and institutional investor activity to determine confidence in the stock from major stakeholders.",
        expected_output="A report summarizing insider buying/selling activity and institutional investment trends.",
        agent=insider_trading_analyst
    )

    # Macroeconomic & Industry Analysis Task
    macro_task = Task(
        description="Assess macroeconomic factors such as interest rates, inflation, and industry trends to determine their impact on the stock’s performance.",
        expected_output="A macroeconomic and industry analysis report highlighting key external factors influencing the stock.",
        agent=macro_industry_analyst
    )

    # Technical Analysis Task
    technical_task = Task(
        description="Perform technical analysis on the stock’s price movement using chart patterns, moving averages, RSI, and MACD indicators to identify trading opportunities.",
        expected_output="A technical analysis report with support/resistance levels, trend insights, and trading signals.",
        agent=technical_analyst
    )

    # Final Decision Task
    final_decision_task = Task(
        description="Compile insights from sentiment analysis, risk assessment, insider trading, macroeconomic trends, and technical analysis to provide a final investment recommendation.",
        expected_output="A comprehensive investment report summarizing all analyses, with a final buy, hold, or sell recommendation.",
        agent=analyst,
        dependencies=[sentiment_task, risk_task, insider_trading_task, macro_task, technical_task]
    )

    crew = Crew(
        agents=[analyst, sentiment, risk_assessor],
        tasks=[sentiment_task, risk_task, final_decision_task],
        process="sequential"
    )

    return crew


def run_analysis(stock_symbol):
    crew = create_crew(stock_symbol)
    result = crew.kickoff()
    return result


def main():
    print(run_analysis("GOOGL"))


if __name__ == "__main__":
    main()
