from tools.yf_tech_analysis_tool import yf_tech_analysis
from tools.yf_fundamental_analysis_tool import yf_fundamental_analysis
from tools.competitor_analysis_tool import competitor_analysis
from base import BaseAgent
from crewai import Agent

class ResearchAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm)
        self.create_agent()

    def create_agent(self):
        self.agent = Agent(
            role='Stock Market Researcher',
            goal='Gather and analyze comprehensive data about the stock (e.g., balance sheet, articles, news, etc.).',
            backstory="You're an experienced stock market researcher with an in-depth understanding of value investing.",
            tools=[yf_tech_analysis, yf_fundamental_analysis, competitor_analysis],
            llm=self.llm
        )