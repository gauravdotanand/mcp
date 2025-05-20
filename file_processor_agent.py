from crewai import Agent
from tools.file_reader import FileReaderTool

class FileProcessorAgent:
    def __init__(self, file_reader_tool: FileReaderTool):
        """
        Initialize the file processor agent.
        
        Args:
            file_reader_tool: Tool for reading and processing files
        """
        self.file_reader_tool = file_reader_tool
        
    def create_agent(self) -> Agent:
        """
        Create and return a CrewAI agent for file processing.
        
        Returns:
            Agent: Configured CrewAI agent
        """
        return Agent(
            role='File Processor',
            goal='Read and extract data from downloaded files',
            backstory="""You are an expert data processor with deep knowledge of file handling
            and data extraction. Your specialty is reading files and extracting meaningful
            information from them.""",
            tools=[self.file_reader_tool],
            verbose=True
        ) 