import random
import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.status import Status
from utils.openai_client import get_openai_client
from utils.ai_helper import get_ai_response

console = Console()

tarot_cards = [
    "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
    "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit",
    "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance",
    "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World"
]

questions = [
    "What's the general energy around me right now?",
    "What's a good area to focus on for personal growth?",
    "What positive transformation is on its way to me?",
    "How can I embrace change in my life?",
    "What should I focus on to improve my relationships?",
    "What guidance do the cards have for my career?",
    "How can I better connect with my intuition?",
    "What steps can I take for personal healing?",
    "What is something exciting coming my way?",
    "How can I best prepare for the future?"
]

ORIGINAL_PROGRESS_PAIRS = [
    ("Interpreting the cards...", "Consulting the spirits..."),
    ("Decoding the cosmic signals...", "Channeling ancient wisdom..."),
    ("Reading the energies...", "Aligning with the universe..."),
    ("Analyzing the symbols...", "Awakening hidden insights..."),
    ("Unraveling the mysteries...", "Summoning ethereal guidance..."),
    ("Connecting the dots...", "Listening to the cosmic hum..."),
    ("Exploring card meanings...", "Drawing on universal energy..."),
    ("Unlocking the secrets...", "Manifesting clarity..."),
    ("Sifting through symbolism...", "Hearing whispers from beyond..."),
    ("Distilling cosmic clues...", "Embracing celestial messages...")
]
progress_pairs = ORIGINAL_PROGRESS_PAIRS.copy()

def get_progress_pair():
    """Return a random progress pair and remove it from the global list."""
    global progress_pairs
    if not progress_pairs:
        progress_pairs = ORIGINAL_PROGRESS_PAIRS.copy()
    pair = random.choice(progress_pairs)
    progress_pairs.remove(pair)
    return pair

def main():
    console.print(Panel(Text("Welcome to the Terminal Tarot Reading App!", justify="center"), title="[bold magenta]Tarot Reader[/bold magenta]"))
    while True:
        sample_questions = random.sample(questions, 3)
        question_text = ""
        for idx, q in enumerate(sample_questions, start=1):
            question_text += f"{idx}. {q}\n"
        
        console.print(Panel(question_text, title="[bold cyan]Choose a Focus for Your Reading[/bold cyan]"))
        
        user_choice = console.input("[bold]Enter the number of your choice (1-3): [/bold]").strip()
        if user_choice not in ["1", "2", "3"]:
            console.print("[bold red]Invalid choice. Please select 1, 2, or 3.[/bold red]")
            continue
        selected_question = sample_questions[int(user_choice)-1]

        drawn_cards = []
        with console.status("[bold yellow]Drawing cards...[/bold yellow]") as status:
            for i in range(3):
                time.sleep(1.5)
                card = random.choice([c for c in tarot_cards if c not in drawn_cards])
                drawn_cards.append(card)
                status.update(f"[bold yellow]Drawing cards... ({i+1}/3)[/bold yellow]")
        
        card_titles = ["1st Card", "2nd Card", "3rd Card"]
        for i, card in enumerate(drawn_cards):
            console.print(Panel(Text(f"- {card}", justify="center"), title=f"[bold yellow]{card_titles[i]}[/bold yellow]"))
            time.sleep(1)

        interpret_msg, consult_msg = get_progress_pair()
        console.print(f"[bold green]{interpret_msg}[/bold green]")
        time.sleep(2)
        console.print(f"[bold green]{consult_msg}[/bold green]")
        time.sleep(1)

        with console.status("[bold blue]Consulting the OpenAI spirits...[/bold blue]"):
            reading = get_ai_response(
                system_message="You are a tarot card reader that provides supportive, concise, and easy-to-understand readings. Focus specifically on answering the user's question using the symbolism of the drawn cards. Provide interpretations that are both meaningful and practical. In 3 sentences or less.",
                user_prompt=f"I have drawn the following tarot cards: {', '.join(drawn_cards)}. The focus question is: '{selected_question}'. Please provide a fun, insightful, and easy-to-understand tarot reading that interprets these cards."
            )
        
        if reading:
            console.print(Panel(Text(reading, justify="left"), title="[bold green]Your Tarot Reading[/bold green]"))

        again = console.input("\n[bold]Would you like another reading? (Y/N): [/bold]").strip().lower()
        if again != 'y':
            console.print("[bold magenta]Thank you for using the Terminal Tarot Reading App. Goodbye![/bold magenta]")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Process interrupted by user. Exiting...[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
