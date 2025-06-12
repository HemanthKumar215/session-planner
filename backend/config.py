# scheduler/backend/config.py

import os

class Config:
    """
    Configuration settings for the backend application.
    Sensitive information should ideally be loaded from environment variables.
    """
    # Base directory for data files
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

    # Path to the biology curriculum JSON file
    CURRICULUM_FILE_PATH = os.path.join(DATA_DIR, 'biology_curriculum.json')

    # Directories for PYQs and Textbooks
    PYQS_DIR = os.path.join(DATA_DIR, 'pyqs')
    TEXTBOOKS_DIR = os.path.join(DATA_DIR, 'textbooks')

    # Groq API Key (loaded from environment variable for security)
    # Ensure you set GROQ_API_KEY in your .env file or system environment variables
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', 'your_default_grok_api_key_if_not_set_in_env')

    # Backend API port
    FLASK_RUN_PORT = os.getenv('FLASK_RUN_PORT', 5000)

    # Add other configuration variables here as your project grows
    # For example:
    # DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///scheduler.db')
    # DEBUG_MODE = os.getenv('DEBUG_MODE', 'True').lower() in ('true', '1', 't')

# You can import this Config class into app.py to access settings:
# from config import Config
# api_key = Config.GROQ_API_KEY