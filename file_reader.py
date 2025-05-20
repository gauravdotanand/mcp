import os
from pathlib import Path
from typing import Optional
from datetime import datetime
import platform

class FileReaderTool:
    def __init__(self, downloads_path: Optional[str] = None):
        """
        Initialize the file reader tool.
        
        Args:
            downloads_path (str, optional): Path to downloads folder. If None, uses default system downloads path.
        """
        if downloads_path:
            self.downloads_path = Path(downloads_path)
        else:
            self.downloads_path = self._get_default_downloads_path()
            
    def _get_default_downloads_path(self) -> Path:
        """
        Get the default downloads path based on the operating system.
        
        Returns:
            Path: Path to the downloads folder
        """
        system = platform.system().lower()
        home = Path.home()
        
        if system == "windows":
            # Windows typically uses "Downloads" in the user's home directory
            return home / "Downloads"
        elif system == "darwin":  # macOS
            # macOS uses "Downloads" in the user's home directory
            return home / "Downloads"
        elif system == "linux":
            # Linux typically uses "Downloads" in the user's home directory
            # Some distributions might use localized names, so we check common variations
            possible_paths = [
                home / "Downloads",
                home / "downloads",
                home / "Téléchargements",  # French
                home / "Descargas",        # Spanish
                home / "Downloads",        # English
            ]
            
            # Return the first existing path
            for path in possible_paths:
                if path.exists():
                    return path
                    
            # If none exist, default to "Downloads"
            return home / "Downloads"
        else:
            # For unknown OS, default to "Downloads" in home directory
            return home / "Downloads"
            
    def get_latest_txt_file(self) -> Optional[Path]:
        """
        Get the path of the latest .txt file in the downloads folder.
        
        Returns:
            Optional[Path]: Path to the latest txt file, or None if no txt files found
        """
        txt_files = list(self.downloads_path.glob("*.txt"))
        if not txt_files:
            return None
            
        # Sort by modification time, newest first
        return max(txt_files, key=lambda x: x.stat().st_mtime)
        
    def read_file_content(self, file_path: Optional[Path] = None) -> str:
        """
        Read content from the specified file or latest txt file.
        
        Args:
            file_path (Optional[Path]): Path to the file to read. If None, reads latest txt file.
            
        Returns:
            str: Content of the file
            
        Raises:
            FileNotFoundError: If no file is found or specified file doesn't exist
        """
        if file_path is None:
            file_path = self.get_latest_txt_file()
            
        if file_path is None:
            raise FileNotFoundError("No .txt files found in downloads folder")
            
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
            
    def extract_data(self, content: str) -> dict:
        """
        Extract structured data from the file content.
        This is a basic implementation - you should customize this based on your file format.
        
        Args:
            content (str): Content of the file
            
        Returns:
            dict: Extracted data
        """
        # Basic implementation - split by lines and create a dictionary
        lines = content.strip().split('\n')
        data = {
            'total_lines': len(lines),
            'content': lines,
            'timestamp': datetime.now().isoformat()
        }
        
        return data 