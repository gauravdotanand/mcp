import os

# Disable CrewAI telemetry
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"

# OpenAI Configuration
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_MODEL_NAME"] = "gpt-4o"  # or "gpt-4" if you have access

# Load environment variables
from dotenv import load_dotenv
load_dotenv() 
#print(os.getenv("OPENAI_API_KEY"))