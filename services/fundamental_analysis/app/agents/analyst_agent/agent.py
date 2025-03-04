from tools.risk_assessment_tool import risk_assessment
from tools.yf_tech_analysis_tool import yf_tech_analysis
from tools.yf_fundamental_analysis_tool import yf_fundamental_analysis
from crewai import Agent
from base import BaseAgent 


class FinancialAnalystAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm)
        self.create_agent()

    def create_agent(self):
        self.agent = Agent(
            role='Financial Analyst',
            goal='Analyze the gathered data and provide investment insights.',
            backstory="You're a seasoned financial analyst skilled in predicting long-term company growth using data.",
            tools=[yf_tech_analysis, yf_fundamental_analysis, risk_assessment],
            llm=self.llm
        )