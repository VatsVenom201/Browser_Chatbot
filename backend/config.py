import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")

if not GROQ_API_KEY or not HF_API_KEY:
    print("WARNING: API keys not loaded propertly. Please set GROQ_API_KEY and HF_API_KEY environment variables.")
