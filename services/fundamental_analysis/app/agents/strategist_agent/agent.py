from tools.sentiment_analysis_tool import sentiment_analysis
from tools.risk_assessment_tool import risk_assessment
from base import BaseAgent
from crewai import Agent

class StrategistAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm)
        self.create_agent()

    def create_agent(self):
        self.agent = Agent(
            role='Investment Strategist',
            goal='Develop a comprehensive investment strategy based on all available data.',
            backstory="You're a renowned investment strategist known for creating tailored investment plans that balance risk and reward.",
            tools=[sentiment_analysis, risk_assessment],
            llm=self.llm
        )