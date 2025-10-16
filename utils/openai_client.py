import os
from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console

console = Console()

def get_openai_client():
    """Loads API key and returns an OpenAI client, or None if the key is not found."""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[bold red]OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.[/bold red]")
        return None
    return OpenAI(api_key=api_key)
