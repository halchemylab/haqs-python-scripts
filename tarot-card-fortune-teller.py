import json
import random
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from utils.ai_helper import get_ai_response

console = Console()

CARD_MEANINGS_PATH = Path(__file__).with_name("tarot-card-meanings.json")

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
    "How can I best prepare for the future?",
    "What should I understand about my current life path?",
    "Where could I use more balance in my daily life?",
    "What lesson am I being invited to learn right now?",
    "How can I make better use of my time and energy?",
    "What part of myself needs more acceptance?",
    "What hidden strength can help me through my current situation?",
    "How can I invite more joy into my life?",
    "What should I release to move forward with more clarity?",
    "How can I improve my relationship with money and security?",
    "What support or connection should I be more open to?"
]

SPREAD_POSITIONS = ["Past", "Present", "Future"]

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


def load_card_meanings():
    """Load and validate the local Major Arcana meaning reference."""
    with CARD_MEANINGS_PATH.open(encoding="utf-8") as meanings_file:
        meanings = json.load(meanings_file)

    missing_cards = [card for card in tarot_cards if card not in meanings]
    incomplete_cards = [
        card
        for card in tarot_cards
        if card in meanings
        and not all(orientation in meanings[card] for orientation in ("upright", "reversed"))
    ]
    if missing_cards or incomplete_cards:
        problems = []
        if missing_cards:
            problems.append(f"missing cards: {', '.join(missing_cards)}")
        if incomplete_cards:
            problems.append(f"missing orientations: {', '.join(incomplete_cards)}")
        raise ValueError(f"Invalid tarot meaning data ({'; '.join(problems)})")

    return meanings


def format_meaning_reference(drawn_cards, meanings):
    """Format only the drawn cards' local meanings for the AI prompt."""
    lines = []
    for position, card in zip(SPREAD_POSITIONS, drawn_cards):
        meaning = meanings[card["name"]][card["orientation"]]
        lines.append(
            f"- {position} — {card['name']} ({card['orientation']}): {meaning}"
        )
    return "\n".join(lines)

def get_progress_pair():
    """Return a random progress pair and remove it from the global list."""
    global progress_pairs
    if not progress_pairs:
        progress_pairs = ORIGINAL_PROGRESS_PAIRS.copy()
    pair = random.choice(progress_pairs)
    progress_pairs.remove(pair)
    return pair

def main():
    card_meanings = load_card_meanings()
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
                card = random.choice([c for c in tarot_cards if c not in [drawn_card["name"] for drawn_card in drawn_cards]])
                orientation = random.choice(["upright", "reversed"])
                drawn_cards.append({"name": card, "orientation": orientation})
                status.update(f"[bold yellow]Drawing cards... ({i+1}/3)[/bold yellow]")
        
        for i, card in enumerate(drawn_cards):
            card_label = card["name"]
            if card["orientation"] == "reversed":
                card_label += " (reversed)"
            console.print(Panel(Text(f"- {card_label}", justify="center"), title=f"[bold yellow]{SPREAD_POSITIONS[i]}[/bold yellow]"))
            time.sleep(1)

        interpret_msg, consult_msg = get_progress_pair()
        console.print(f"[bold green]{interpret_msg}[/bold green]")
        time.sleep(2)
        console.print(f"[bold green]{consult_msg}[/bold green]")
        time.sleep(1)

        with console.status("[bold blue]Consulting the spirits...[/bold blue]"):
            card_summary = ", ".join(
                f"{position}: {card['name']} ({card['orientation']})"
                for position, card in zip(SPREAD_POSITIONS, drawn_cards)
            )
            meaning_reference = format_meaning_reference(drawn_cards, card_meanings)
            reading = get_ai_response(
                system_message="You are a compassionate but candid tarot card reader. Treat the supplied local card meanings as the canonical interpretation guide and connect them to the user's question and spread positions without contradicting them. Name difficult themes clearly when the cards support them; do not soften every warning into generic growth, force a positive conclusion, or catastrophize. Present the reading as symbolic reflection rather than certain prediction, and offer practical guidance grounded in what the user can observe or influence. Use clear, direct language in 3 sentences or less.",
                user_prompt=f"I have drawn the following three-card Past / Present / Future tarot spread: {card_summary}. The focus question is: '{selected_question}'.\n\nLocal meaning reference:\n{meaning_reference}\n\nPlease provide an engaging, insightful, and easy-to-understand tarot reading. Interpret each card in its spread position and orientation.",
                temperature=0.4,
                display_errors=False
            )
        
        if reading:
            console.print(Panel(Text(reading, justify="left"), title="[bold green]Your Tarot Reading[/bold green]"))
        else:
            console.print("[bold red]The reading could not be completed. Please check your setup and try again.[/bold red]")

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
