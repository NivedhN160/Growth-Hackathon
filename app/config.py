import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is required")

GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
OUTPUT_DIR = "output"
MAX_CONTENT_CHARS = 12000
