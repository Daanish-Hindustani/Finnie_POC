from crewai import Agent, Task, Crew, Process
from langchain.llms import Ollama
from tools.yf_tech_analysis_tool import yf_tech_analysis
from tools.yf_fundamental_analysis_tool import yf_fundamental_analysis
from tools.sentiment_analysis_tool import sentiment_analysis
from tools.competitor_analysis_tool import competitor_analysis
from tools.risk_assessment_tool import risk_assessment
from analyst_agent.agent import FinancialAnalystAgent
from researcher_agent.agent import ResearchAgent
from sentiment_analyst_agent.agent import SentimentAnalystAgent
from strategist_agent.agent import StrategistAgent

class StockAnalysisCrew:
    
    def __init__(self, stock_symbol: str):
        self.stock_symbol = stock_symbol
        self.llm = Ollama(model="tinyllama")

    def create_crew(self):
        # Create agents
        researcher = ResearchAgent(self.llm).agent
        analyst = FinancialAnalystAgent(self.llm).agent
        sentiment_analyst = SentimentAnalystAgent(self.llm).agent
        strategist = StrategistAgent(self.llm).agent

        # Define tasks
        research_task = Task(
            description=f"Research {self.stock_symbol} using fundamental analysis tools. Provide a comprehensive summary of key metrics, including chart patterns, financial ratios, and competitor analysis.",
            agent=researcher
        )

        sentiment_task = Task(
            description=f"Analyze the market sentiment for {self.stock_symbol} using news and social media data. Evaluate how current sentiment might affect the stock's performance.",
            agent=sentiment_analyst
        )

        analysis_task = Task(
            description=f"Synthesize the research data and sentiment analysis for {self.stock_symbol}. Conduct a thorough risk assessment and provide a detailed analysis of the stock's potential.",
            agent=analyst
        )

        strategy_task = Task(
            description=f"Based on all the gathered information about {self.stock_symbol}, develop a comprehensive investment strategy. Consider various scenarios and provide actionable recommendations for different investor profiles.",
            agent=strategist
        )

        # Create Crew
        crew = Crew(
            agents=[researcher, sentiment_analyst, analyst, strategist],
            tasks=[research_task, sentiment_task, analysis_task, strategy_task],
            process=Process.parallel
        )

        return crew
    
    def run_analysis(self):
        crew = self.create_crew()
        result = crew.kickoff()
        return result
