import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', None)
OPENAI_API_TYPE = os.environ.get('OPENAI_API_TYPE', None)
OPENAI_API_BASE = os.environ.get('OPENAI_API_BASE', None)
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', None)
OPENAI_API_VERSION = os.environ.get('OPENAI_API_VERSION', None)

if OPENAI_API_KEY is None:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")
