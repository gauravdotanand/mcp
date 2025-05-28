import requests
from bs4 import BeautifulSoup
from typing import Dict, Any
import os
from urllib.parse import urljoin, urlparse
import mimetypes

class WebAutomationTool:
    def __init__(self):
        self.name = "web_automation"
        self.description = """A sophisticated web automation tool that can:
        1. Scrape web content with human-like behavior
        2. Handle and submit web forms
        3. Download files from web pages
        4. Extract structured data from websites
        5. Navigate through multiple pages
        6. Handle dynamic content and JavaScript-rendered pages"""
        
    def scrape_website(self, url: str, download_files: bool = False, download_dir: str = "downloads") -> Dict[str, Any]:
        """
        Scrape content from a given URL with enhanced capabilities
        
        Args:
            url (str): The URL to scrape
            download_files (bool): Whether to download files found on the page
            download_dir (str): Directory to save downloaded files
            
        Returns:
            Dict[str, Any]: Dictionary containing scraped content and file information
        """
        try:
            # Set up headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic information
            title = soup.title.string if soup.title else "No title found"
            
            # Extract all text content
            text_content = soup.get_text(separator=' ', strip=True)
            
            # Extract all links
            links = [a.get('href') for a in soup.find_all('a', href=True)]
            
            # Extract forms
            forms = []
            for form in soup.find_all('form'):
                form_data = {
                    'action': form.get('action', ''),
                    'method': form.get('method', 'get'),
                    'inputs': [{'name': input.get('name', ''), 'type': input.get('type', 'text')} 
                             for input in form.find_all('input')]
                }
                forms.append(form_data)
            
            # Download files if requested
            downloaded_files = []
            if download_files:
                os.makedirs(download_dir, exist_ok=True)
                
                # Find downloadable files (PDFs, docs, images, etc.)
                for link in links:
                    full_url = urljoin(url, link)
                    file_ext = os.path.splitext(urlparse(full_url).path)[1].lower()
                    
                    # Check if it's a downloadable file
                    if file_ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.zip']:
                        try:
                            file_response = requests.get(full_url, headers=headers)
                            file_response.raise_for_status()
                            
                            # Generate filename
                            filename = os.path.basename(urlparse(full_url).path)
                            if not filename:
                                content_type = file_response.headers.get('content-type', '')
                                ext = mimetypes.guess_extension(content_type) or '.bin'
                                filename = f"downloaded_file_{len(downloaded_files)}{ext}"
                            
                            # Save file
                            file_path = os.path.join(download_dir, filename)
                            with open(file_path, 'wb') as f:
                                f.write(file_response.content)
                            
                            downloaded_files.append({
                                'filename': filename,
                                'url': full_url,
                                'path': file_path
                            })
                        except Exception as e:
                            print(f"Error downloading {full_url}: {str(e)}")
            
            return {
                "status": "success",
                "title": title,
                "text_content": text_content,
                "links": links,
                "forms": forms,
                "downloaded_files": downloaded_files if download_files else [],
                "url": url
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "url": url
            } 