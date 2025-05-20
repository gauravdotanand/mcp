from crewai import Crew
from agents.web_scraper_agent import WebScraperAgent
from agents.file_processor_agent import FileProcessorAgent
from tasks.web_scraping_tasks import WebScrapingTasks
from tools.file_reader import FileReaderTool

class WebScrapingCrew:
    def __init__(self, selenium_tool, downloads_path: str = None):
        """
        Initialize the web scraping crew.
        
        Args:
            selenium_tool: Your existing Selenium tool for web interaction
            downloads_path: Optional path to downloads folder
        """
        self.selenium_tool = selenium_tool
        self.file_reader_tool = FileReaderTool(downloads_path)
        
        # Initialize agents
        self.web_scraper = WebScraperAgent(selenium_tool).create_agent()
        self.file_processor = FileProcessorAgent(self.file_reader_tool).create_agent()
        
    def run(self, url: str, download_button_selector: str = None) -> dict:
        """
        Run the web scraping and file processing workflow.
        
        Args:
            url: URL to visit
            download_button_selector: Optional CSS selector for the download button
            
        Returns:
            dict: Extracted data from the downloaded file
        """
        # Create tasks
        scraping_task = WebScrapingTasks.create_scraping_task(
            self.web_scraper,
            url,
            download_button_selector
        )
        
        processing_task = WebScrapingTasks.create_file_processing_task(
            self.file_processor
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[self.web_scraper, self.file_processor],
            tasks=[scraping_task, processing_task],
            verbose=True
        )
        
        result = crew.kickoff()
        return result 