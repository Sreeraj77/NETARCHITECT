import os
from dotenv import load_dotenv

print("Loading config.py...")

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print("API Key found:", GEMINI_API_KEY is not None)

if not GEMINI_API_KEY:
    raise ValueError("Gemini API Key not found.")