from crewai import Agent
from langchain.llms import Ollama

class BaseAgent:
    def __init__(self, llm):
        self.llm = llm
        self.agent = None

    def create_agent(self):
        raise NotImplementedError("Subclasses must implement this method.")