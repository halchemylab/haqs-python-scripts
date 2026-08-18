import random
import time
from rich.console import Console
from rich.panel import Panel
from rich.markup import escape
import configparser
from utils.message_handler import MessageHandler
from utils.csv_helper import read_csv
from utils.ai_helper import get_ai_response

console = Console()

SEARCH_MESSAGES = [
    "Searching ancient texts...",
    "Consulting the old masters...",
    "Exploring philosophical texts...",
    "Diving into the archive...",
    "Dusting off manuscripts...",
    "Gathering source-language wisdom...",
    "Seeking a compact passage...",
    "Unveiling a primary-text fragment..."
]

INTERPRETATION_MESSAGES = [
    "Translating and interpreting...",
    "Reading the original closely...",
    "Contemplating the passage...",
    "Analyzing the source text...",
    "Extracting the essence...",
    "Interpreting the message...",
    "Unraveling the philosophy...",
    "Processing the old wording...",
    "Reflecting on the meaning...",
    "Finding the argument inside the line..."
]

LANGUAGE_DISPLAY = {
    "latin": "Latin",
    "classical chinese": "Classical Chinese",
}

def normalize_language(language):
    return LANGUAGE_DISPLAY.get(language.lower(), language)

def match_language(user_input, language_mappings):
    """Find the language from user input."""
    if not user_input:
        return None
    return language_mappings.get(user_input.lower())

def generate_language_mappings(languages):
    """Generate mappings for the available source languages."""
    mappings = {}
    for language in languages:
        normalized = language.lower()
        mappings[normalized] = language
        mappings[normalize_language(language).lower()] = language

    mappings["0"] = "classical chinese"
    mappings["1"] = "latin"
    mappings["latin"] = "latin"
    mappings["chinese"] = "classical chinese"
    mappings["classical"] = "classical chinese"
    mappings["classical chinese"] = "classical chinese"
    return mappings

def display_random_quote(quotes, search_message_handler, interpretation_message_handler, language=None):
    if not quotes:
        return
    filtered_quotes = [
        q for q in quotes
        if language is None or q["language"].lower() == language.lower()
    ]
    if not filtered_quotes:
        console.print(f"No quotes found for language: {language}", style="bold red")
        return

    selected_quote = random.choice(filtered_quotes)
    
    with console.status(search_message_handler.get_random_message(), spinner="dots"):
        time.sleep(3)
    
    quote_text = f'[italic]{escape(selected_quote["original"])}[/italic]'
    author_text = (
        f'- [bold]{escape(selected_quote["author"])}[/bold], '
        f'{escape(selected_quote["work"])} '
        f'([cyan]{escape(normalize_language(selected_quote["language"]))}[/cyan])'
    )
    
    console.print(Panel(f"{quote_text}\n{author_text}", title="[bold cyan]Original Philosophy Quote[/bold cyan]", expand=False))
    
    with console.status(interpretation_message_handler.get_random_message(), spinner="bouncingBar"):
        explanation = get_ai_response(
            system_message=(
                "You are a philosophical interpreter with expertise in Latin and Classical Chinese texts. "
                "Provide a clear, faithful English translation, then offer a concise philosophical "
                "interpretation grounded in the quoted passage and its attributed work. Preserve ambiguity "
                "where appropriate, distinguish interpretation from literal meaning, and avoid unsupported "
                "historical claims."
            ),
            user_prompt=(
                "Interpret this original-language philosophical quote.\n\n"
                f"Original: {selected_quote['original']}\n"
                f"Author: {selected_quote['author']}\n"
                f"Work: {selected_quote['work']}\n"
                f"Language: {normalize_language(selected_quote['language'])}\n\n"
                "Respond with two short parts:\n"
                "Translation: one concise English rendering.\n"
                "Interpretation: two condensed sentences on the philosophical meaning."
            ),
            max_tokens=180,
            temperature=0.4
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
            languages = sorted(list(set(q["language"] for q in quotes)))
            language_mappings = generate_language_mappings(languages)
            
            search_message_handler = MessageHandler(SEARCH_MESSAGES)
            interpretation_message_handler = MessageHandler(INTERPRETATION_MESSAGES)
            
            quick_inputs = "'0' (Classical Chinese), '1' (Latin)"
            console.print(f"Quick inputs: {quick_inputs}")

            while True:
                language_input = console.input("Enter language number (or press Enter for random): ")
                matched_language = match_language(language_input, language_mappings)
                display_random_quote(
                    quotes,
                    search_message_handler,
                    interpretation_message_handler,
                    matched_language
                )
                
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
