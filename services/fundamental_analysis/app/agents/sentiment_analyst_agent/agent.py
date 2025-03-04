from tools.sentiment_analysis_tool import sentiment_analysis
from base import BaseAgent
from crewai import Agent

class SentimentAnalystAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm)
        self.create_agent()

    def create_agent(self):
        self.agent = Agent(
            role='Sentiment Analyst',
            goal='Analyze market sentiment and its potential impact on the stock.',
            backstory="You're an expert in behavioral finance and sentiment analysis, capable of gauging market emotions and their effects on stock performance.",
            tools=[sentiment_analysis],
            llm=self.llm
        )