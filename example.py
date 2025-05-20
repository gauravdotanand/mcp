from crew.web_scraping_crew import WebScrapingCrew
from your_selenium_tool import YourSeleniumTool  # Replace with your actual Selenium tool

def main():
    # Initialize your Selenium tool
    selenium_tool = YourSeleniumTool()
    
    # Create the web scraping crew
    crew = WebScrapingCrew(
        selenium_tool=selenium_tool,
        downloads_path="/path/to/downloads"  # Optional: specify custom downloads path
    )
    
    # Run the crew with example parameters
    result = crew.run(
        url="https://example.com/download-page",
        download_button_selector="#download-button"  # Optional: CSS selector for download button
    )
    
    # Print the results
    print("Extracted data:", result)

if __name__ == "__main__":
    main() 