import random
import csv
import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
import configparser
from utils.openai_client import get_openai_client
from utils.message_handler import MessageHandler
from utils.csv_helper import read_csv
from utils.ai_helper import get_ai_response

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
        explanation = get_ai_response(
            system_message="You are an assistant that explains quotes.",
            user_prompt=f"Can you explain this quote: '{selected_quote['quote']}' by {selected_quote['author']} in 2 condensed sentences max?"
        )
        time.sleep(2)

    if explanation:
        console.print(Panel(explanation, title="[bold green]Interpretation[/bold green]", expand=False))
    console.print()

if __name__ == "__main__":
    try:
        
        config = configparser.ConfigParser()
        config.read('config.ini')
        paths = config['Paths']
        quotes_file = paths.get('quotes_file', 'data/quotes.csv')

        console.print("[bold cyan]Welcome to the Philosophy Quotes Generator![/bold cyan]")
        
        quotes = read_csv(quotes_file, as_dict=True)
        if quotes:
            eras = sorted(list(set(q["era"] for q in quotes)))
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
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Process interrupted by user. Exiting...[/bold yellow]")
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        console.print(f"[bold red]Configuration Error: {e}. Please check your config.ini file.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")