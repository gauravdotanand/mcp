import time
from typing import Optional, Tuple, List, Dict, Any, Union
import logging
from dataclasses import dataclass
from py3270 import Emulator
from enum import Enum
import re
import os
import signal
import sys
from datetime import datetime

# Configure logging for headless operation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tn3270.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ScreenStatus(Enum):
    """Enum for screen status indicators"""
    READY = "READY"
    ERROR = "ERROR"
    LOGIN = "LOGIN"
    PASSWORD = "PASSWORD"
    UNKNOWN = "UNKNOWN"
    SYSTEM_ERROR = "SYSTEM ERROR"
    INVALID_COMMAND = "INVALID COMMAND"
    NOT_AUTHORIZED = "NOT AUTHORIZED"

@dataclass
class ScreenPosition:
    """Class for screen position coordinates"""
    row: int
    col: int

@dataclass
class TN3270Config:
    """Configuration for TN3270 connection"""
    host: str
    port: int
    username: str
    password: str
    timeout: int = 30
    visible: bool = False
    lu_name: Optional[str] = None
    ssl: bool = False
    retry_attempts: int = 3
    retry_delay: int = 5
    command_timeout: int = 60
    screen_wait_time: int = 2
    max_screen_history: int = 100
    log_screens: bool = True
    screen_log_dir: str = "screen_logs"

class TN3270Error(Exception):
    """Base exception for TN3270 errors"""
    pass

class ConnectionError(TN3270Error):
    """Exception for connection-related errors"""
    pass

class LoginError(TN3270Error):
    """Exception for login-related errors"""
    pass

class CommandError(TN3270Error):
    """Exception for command execution errors"""
    pass

class TimeoutError(TN3270Error):
    """Exception for timeout-related errors"""
    pass

class TN3270Connector:
    def __init__(self, config: TN3270Config):
        """
        Initialize the TN3270 connector with configuration
        
        Args:
            config (TN3270Config): Configuration object containing connection details
        """
        self.config = config
        self.emulator = None
        self.connected = False
        self._screen_buffer = []
        self._last_command = None
        self._last_response = None
        self._command_history = []
        self._session_start_time = None
        
        # Create screen log directory if needed
        if self.config.log_screens:
            os.makedirs(self.config.screen_log_dir, exist_ok=True)
            
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle termination signals"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown")
        self.disconnect()
        sys.exit(0)
        
    def _log_screen(self, screen_content: str, prefix: str = "") -> None:
        """Log screen content to file"""
        if not self.config.log_screens:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.config.screen_log_dir}/{prefix}_{timestamp}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write(screen_content)
        except Exception as e:
            logger.error(f"Failed to log screen: {str(e)}")
            
    def _validate_screen(self, screen: str) -> bool:
        """Validate screen content for common error conditions"""
        screen_upper = screen.upper()
        
        if "SYSTEM ERROR" in screen_upper:
            raise CommandError("System error detected")
        if "NOT AUTHORIZED" in screen_upper:
            raise CommandError("Not authorized to perform operation")
        if "INVALID COMMAND" in screen_upper:
            raise CommandError("Invalid command")
            
        return True
        
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
        
    def connect(self) -> bool:
        """Establish connection to the mainframe"""
        self._session_start_time = datetime.now()
        
        for attempt in range(self.config.retry_attempts):
            try:
                # Initialize the emulator with only supported parameters
                self.emulator = Emulator(
                    visible=self.config.visible,
                    timeout=self.config.timeout
                )
                
                # Build connection string
                conn_str = f"{self.config.host}:{self.config.port}"
                if self.config.lu_name:
                    conn_str += f"/LU:{self.config.lu_name}"
                if self.config.ssl:
                    conn_str += "/SSL"
                
                # Connect to the mainframe
                self.emulator.connect(conn_str)
                logger.info("Successfully connected to mainframe")
                
                # Wait for the screen to be ready
                self.emulator.wait_for_field()
                
                # Login if credentials are provided
                if self.config.username and self.config.password:
                    self._login()
                
                self.connected = True
                return True
                
            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {str(e)}")
                if self.emulator:
                    self.emulator.terminate()
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(self.config.retry_delay)
                else:
                    raise ConnectionError(f"Failed to connect after {self.config.retry_attempts} attempts")
        
        return False
        
    def _login(self) -> None:
        """Handle the login process"""
        try:
            # Wait for the login screen
            self.emulator.wait_for_field()
            
            # Check if we're at the login screen
            if not self._is_login_screen():
                raise LoginError("Not at login screen")
            
            # Enter username
            self.emulator.send_string(self.config.username)
            self.emulator.send_enter()
            
            # Wait for password field
            self.emulator.wait_for_field()
            
            # Check if we're at the password screen
            if not self._is_password_screen():
                raise LoginError("Not at password screen")
            
            # Enter password
            self.emulator.send_string(self.config.password)
            self.emulator.send_enter()
            
            # Wait for the main screen
            self.emulator.wait_for_field()
            
            # Verify login success
            if not self._is_ready_screen():
                raise LoginError("Login failed - not at ready screen")
            
            logger.info("Successfully logged in")
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            raise LoginError(f"Login failed: {str(e)}")
            
    def _is_login_screen(self) -> bool:
        """Check if current screen is login screen"""
        screen = self.get_screen_content()
        return "LOGON" in screen.upper() or "USERID" in screen.upper()
        
    def _is_password_screen(self) -> bool:
        """Check if current screen is password screen"""
        screen = self.get_screen_content()
        return "PASSWORD" in screen.upper()
        
    def _is_ready_screen(self) -> bool:
        """Check if current screen is ready screen"""
        screen = self.get_screen_content()
        return "READY" in screen.upper()
        
    def _check_connection(self) -> bool:
        """
        Check if the connection is still active
        
        Returns:
            bool: True if connection is active
        """
        if not self.emulator or not self.connected:
            return False
            
        try:
            # Try to get screen content to check connection
            self.emulator.string_get(1, 1, 1, 1)
            return True
        except Exception:
            self.connected = False
            return False

    def send_command(self, command: str, wait_time: Optional[int] = None) -> str:
        """
        Send a command to the mainframe and get the response
        
        Args:
            command (str): Command to send
            wait_time (Optional[int]): Time to wait for response in seconds
            
        Returns:
            str: Response from the mainframe
        """
        if not self._check_connection():
            raise ConnectionError("Not connected to mainframe")
            
        wait_time = wait_time or self.config.screen_wait_time
        start_time = time.time()
        
        try:
            self._last_command = command
            self._command_history.append((datetime.now(), command))
            
            self.emulator.send_string(command)
            self.emulator.send_enter()
            
            # Wait for response with timeout
            while time.time() - start_time < self.config.command_timeout:
                time.sleep(wait_time)
                response = self.get_screen_content()
                
                # Validate screen content
                self._validate_screen(response)
                
                # Check if command has completed
                if self._is_command_complete(response):
                    self._last_response = response
                    self._screen_buffer.append(response)
                    self._log_screen(response, f"cmd_{command.replace(' ', '_')}")
                    
                    # Keep only last N screens in buffer
                    if len(self._screen_buffer) > self.config.max_screen_history:
                        self._screen_buffer.pop(0)
                        
                    return response
                    
            raise TimeoutError(f"Command timed out after {self.config.command_timeout} seconds")
            
        except Exception as e:
            logger.error(f"Failed to send command: {str(e)}")
            self.connected = False  # Mark as disconnected on error
            raise CommandError(f"Command failed: {str(e)}")
            
    def _is_command_complete(self, screen: str) -> bool:
        """Check if command has completed execution"""
        # Add your specific command completion indicators here
        return "READY" in screen or "ERROR" in screen
        
    def get_screen_content(self) -> str:
        """Get the current screen content"""
        if not self._check_connection():
            raise ConnectionError("Not connected to mainframe")
            
        try:
            return self.emulator.string_get(1, 1, 24, 80)
        except Exception as e:
            logger.error(f"Failed to get screen content: {str(e)}")
            self.connected = False  # Mark as disconnected on error
            raise
            
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        if not self._session_start_time:
            return {}
            
        duration = datetime.now() - self._session_start_time
        return {
            "start_time": self._session_start_time,
            "duration": duration,
            "commands_executed": len(self._command_history),
            "screens_captured": len(self._screen_buffer)
        }
        
    def disconnect(self) -> None:
        """Disconnect from the mainframe"""
        try:
            if self.emulator:
                # Log final screen if still connected
                if self.connected:
                    try:
                        self._log_screen(self.get_screen_content(), "disconnect")
                    except Exception:
                        pass  # Ignore errors during final screen capture
                    
                    # Log session stats
                    stats = self.get_session_stats()
                    logger.info(f"Session statistics: {stats}")
                
                try:
                    self.emulator.terminate()
                except Exception as e:
                    logger.error(f"Error during emulator termination: {str(e)}")
                finally:
                    self.emulator = None
                    self.connected = False
                    logger.info("Successfully disconnected from mainframe")
        except Exception as e:
            logger.error(f"Failed to disconnect: {str(e)}")
            self.connected = False
            self.emulator = None
            raise

# Example usage
if __name__ == "__main__":
    # Create configuration for headless operation
    config = TN3270Config(
        host="your-mainframe-host",
        port=23,
        username="your-username",
        password="your-password",
        visible=False,  # Always False for headless operation
        ssl=True,
        retry_attempts=3,
        retry_delay=5,
        command_timeout=60,
        screen_wait_time=2,
        log_screens=True,
        screen_log_dir="screen_logs"
    )
    
    # Use context manager for automatic connection/disconnection
    with TN3270Connector(config) as connector:
        # Send a command
        response = connector.send_command("D T,ALL")
        print("Command response:", response)
        
        # Get session statistics
        stats = connector.get_session_stats()
        print("Session statistics:", stats) 