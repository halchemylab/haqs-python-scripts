import random
import csv
from dotenv import load_dotenv
import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
import configparser
from utils.openai_client import get_openai_client

console = Console()

SEARCH_MESSAGES = [
    "Searching ancient scrolls...",
    "Finding the right quote for you...",
    "Looking through thousands of years of wisdom...",
    "Consulting the great thinkers...",
    "Exploring philosophical depths...",
    "Diving into the archives of wisdom...",
    "Dusting off ancient manuscripts...",
    "Gathering timeless insights...",
    "Seeking profound thoughts...",
    "Unveiling philosophical treasures..."
]

INTERPRETATION_MESSAGES = [
    "Deciphering the meaning...",
    "Understanding the wisdom...",
    "Contemplating the depths...",
    "Analyzing the insight...",
    "Extracting the essence...",
    "Interpreting the message...",
    "Unraveling the philosophy...",
    "Processing the wisdom...",
    "Reflecting on meaning...",
    "Discovering hidden insights..."
]

class MessageHandler:
    """Handles lists of messages to avoid repetition."""
    def __init__(self, messages):
        self.messages = messages
        self.used_messages = []

    def get_random_message(self):
        """Get a random message and track usage."""
        if not self.messages or len(self.used_messages) >= len(self.messages):
            self.used_messages = []
        
        available_messages = [m for m in self.messages if m not in self.used_messages]
        message = random.choice(available_messages)
        self.used_messages.append(message)
        return message

def match_era(user_input, era_mappings):
    """Find the era from user input."""
    if not user_input:
        return None
    return era_mappings.get(user_input.lower())

def generate_era_mappings(eras):
    """Generate mappings from the first letter and full name of each era."""
    mappings = {}
    for era in eras:
        mappings[era[0].lower()] = era
        mappings[era.lower()] = era
    return mappings

def load_quotes(filename):
    quotes = []
    eras = set()
    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                quotes.append(row)
                eras.add(row["era"])
    except FileNotFoundError:
        console.print(f"[bold red]Error: The quotes file was not found at {filename}[/bold red]")
        return [], []
    return quotes, sorted(list(eras))

def get_ai_explanation(quote, author):
    client = get_openai_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that explains quotes."},
            {"role": "user", "content": f"Can you explain this quote: '{quote}' by {author} in 2 condensed sentences max?"}
        ]
    )
    return response.choices[0].message.content.strip()

def display_random_quote(quotes, search_message_handler, interpretation_message_handler, era=None):
    if not quotes:
        return
    filtered_quotes = [q for q in quotes if era is None or q["era"].lower() == era.lower()]
    if not filtered_quotes:
        console.print(f"No quotes found for era: {era}", style="bold red")
        return

    selected_quote = random.choice(filtered_quotes)
    
    with console.status(search_message_handler.get_random_message(), spinner="dots"):
        time.sleep(3)
    
    quote_text = f'"[italic]{selected_quote["quote"]}[/italic]"'
    author_text = f'- [bold]{selected_quote["author"]}[/bold] ({selected_quote["era"]})'
    
    console.print(Panel(f"{quote_text}\n{author_text}", title="[bold cyan]Philosophy Quote[/bold cyan]", expand=False))
    
    with console.status(interpretation_message_handler.get_random_message(), spinner="bouncingBar"):
        explanation = get_ai_explanation(selected_quote["quote"], selected_quote["author"])
        time.sleep(2)

    console.print(Panel(explanation, title="[bold green]Interpretation[/bold green]", expand=False))
    console.print()

if __name__ == "__main__":
    load_dotenv()  # Load environment variables
    
    config = configparser.ConfigParser()
    config.read('config.ini')
    paths = config['Paths']
    quotes_file = paths.get('quotes_file', 'data/quotes.csv')

    console.print("[bold cyan]Welcome to the Philosophy Quotes Generator![/bold cyan]")
    
    quotes, eras = load_quotes(quotes_file)
    if quotes:
        era_mappings = generate_era_mappings(eras)
        
        search_message_handler = MessageHandler(SEARCH_MESSAGES)
        interpretation_message_handler = MessageHandler(INTERPRETATION_MESSAGES)
        
        quick_inputs = ', '.join([f"'{era[0].lower()}' ({era})" for era in eras])
        console.print(f"Quick inputs: {quick_inputs}")

        while True:
            era_input = console.input("Enter era (or press Enter for random): ")
            matched_era = match_era(era_input, era_mappings)
            display_random_quote(quotes, search_message_handler, interpretation_message_handler, matched_era)
            
            continue_choice = console.input("Would you like another quote? (Y/N): ").lower()
            if continue_choice != 'y':
                console.print("[bold cyan]Goodbye![/bold cyan]")
                break
