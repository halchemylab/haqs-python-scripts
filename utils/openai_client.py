import os
from openai import OpenAI
from dotenv import load_dotenv

def get_openai_client():
    """Loads API key and returns an OpenAI client."""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    return OpenAI(api_key=api_key)
