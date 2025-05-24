import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ElevenLabs configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")

# Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Application configuration
DEBUG = os.getenv("DEBUG", "True") == "True"
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

# File paths
DATA_DIR = BASE_DIR / "data" / "pune_university"
VECTOR_STORE_DIR = BASE_DIR / "vector_stores"
AUDIO_CACHE_DIR = BASE_DIR / "static" / "audio_cache"

# Create directories if they don't exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Quick access categories
QUICK_ACCESS_CATEGORIES = [
    "Admission Process",
    "Exam Schedule", 
    "Fee Structure", 
    "Scholarship Info"
]