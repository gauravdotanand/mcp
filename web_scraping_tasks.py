from crewai import Task
from typing import Optional

class WebScrapingTasks:
    @staticmethod
    def create_scraping_task(agent, url: str, download_button_selector: Optional[str] = None) -> Task:
        """
        Create a task for web scraping and file downloading.
        
        Args:
            agent: The web scraper agent
            url: URL to visit
            download_button_selector: CSS selector for the download button
            
        Returns:
            Task: Configured CrewAI task
        """
        return Task(
            description=f"""Visit the website at {url} and download the required file.
            If a download button selector is provided ({download_button_selector}), use it to trigger the download.
            Ensure the file is successfully downloaded to the downloads folder.""",
            agent=agent
        )
        
    @staticmethod
    def create_file_processing_task(agent) -> Task:
        """
        Create a task for processing the downloaded file.
        
        Args:
            agent: The file processor agent
            
        Returns:
            Task: Configured CrewAI task
        """
        return Task(
            description="""Find the latest downloaded .txt file in the downloads folder,
            read its contents, and extract all relevant data. Return the extracted data
            in a structured format.""",
            agent=agent
        ) 