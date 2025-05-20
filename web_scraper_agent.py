from crewai import Agent
from typing import Optional

class WebScraperAgent:
    def __init__(self, selenium_tool):
        """
        Initialize the web scraper agent.
        
        Args:
            selenium_tool: Your existing Selenium tool for web interaction
        """
        self.selenium_tool = selenium_tool
        
    def create_agent(self) -> Agent:
        """
        Create and return a CrewAI agent for web scraping.
        
        Returns:
            Agent: Configured CrewAI agent
        """
        return Agent(
            role='Web Scraper',
            goal='Navigate websites and download required files',
            backstory="""You are an expert web scraper with deep knowledge of web automation.
            Your specialty is navigating complex websites and downloading files efficiently.""",
            tools=[self.selenium_tool],
            verbose=True
        ) 