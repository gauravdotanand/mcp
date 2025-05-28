import autogen
from web_scraping_tool import WebAutomationTool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration for the agents
config_list = [
    {
        "model": "gpt-4",
        "api_key": os.getenv("OPENAI_API_KEY")
    }
]

# Create the web automation tool
web_automation_tool = WebAutomationTool()

# Define the assistant that will use the web automation tool
web_researcher = autogen.AssistantAgent(
    name="Web_Researcher",
    llm_config={"config_list": config_list},
    system_message="""You are a web research and automation assistant that can:
    1. Scrape and analyze web content with human-like behavior
    2. Handle and submit web forms
    3. Download files from web pages
    4. Extract structured data from websites
    5. Navigate through multiple pages
    6. Handle dynamic content
    
    You have access to a sophisticated web automation tool that can perform these tasks.
    Use this tool to gather information, download files, and interact with web forms as needed."""
)

# Define the user proxy
user_proxy = autogen.UserProxyAgent(
    name="User_Proxy",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"work_dir": "workspace"},
    llm_config={"config_list": config_list},
    system_message="""A human user that needs help with web research, automation, and file downloading tasks."""
)

# Register the web automation tool with the assistant
web_researcher.register_function(
    function_map={
        "scrape_website": web_automation_tool.scrape_website
    }
)

def main():
    # Example conversation
    user_proxy.initiate_chat(
        web_researcher,
        message="""Please help me research information about Python programming.
        Start by scraping the Python.org website, download any relevant PDF documentation,
        and provide a summary of what you find. Also, check if there are any forms
        that might be useful for the research."""
    )

if __name__ == "__main__":
    main() 