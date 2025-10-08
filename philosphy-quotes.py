import random
import csv
from dotenv import load_dotenv
import os
import time
from openai import OpenAI



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

def load_quotes(filename="quotes.csv"):
    quotes = []
    eras = set()
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            quotes.append(row)
            eras.add(row["era"])
    return quotes, sorted(list(eras))

def get_ai_explanation(quote, author):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that explains quotes."},
            {"role": "user", "content": f"Can you explain this quote: '{quote}' by {author} in 2 condensed sentences max?"}
        ]
    )
    return response.choices[0].message.content.strip()

def display_random_quote(quotes, search_message_handler, interpretation_message_handler, era=None):
    filtered_quotes = [q for q in quotes if era is None or q["era"].lower() == era.lower()]
    if not filtered_quotes:
        print(f"No quotes found for era: {era}")
        return

    time.sleep(1)
    selected_quote = random.choice(filtered_quotes)
    
    # Display first progress message and wait
    print(f"\n{search_message_handler.get_random_message()}")
    time.sleep(3)
    
    # Display the quote
    print(f'\n"{selected_quote["quote"]}"\n- {selected_quote["author"]} ({selected_quote["era"]})')
    time.sleep(4)
    
    # Display second progress messages and wait - get two different messages
    first_msg = interpretation_message_handler.get_random_message()
    second_msg = interpretation_message_handler.get_random_message()
    print(f"\n{first_msg}")
    time.sleep(2)
    print(f"{second_msg}")  # No newline before second message
    time.sleep(2)
    
    # Get and display AI explanation
    explanation = get_ai_explanation(selected_quote["quote"], selected_quote["author"])
    print()
    print(explanation)
    print()  # Add empty line after explanation

if __name__ == "__main__":
    load_dotenv()  # Load environment variables
    print("Welcome to the Philosophy Quotes Generator!")
    
    quotes, eras = load_quotes()
    era_mappings = generate_era_mappings(eras)
    
    search_message_handler = MessageHandler(SEARCH_MESSAGES)
    interpretation_message_handler = MessageHandler(INTERPRETATION_MESSAGES)
    
    quick_inputs = ', '.join([f"'{era[0].lower()}' ({era})" for era in eras])
    print(f"Quick inputs: {quick_inputs}")

    while True:
        era_input = input("Enter era (or press Enter for random): ")
        matched_era = match_era(era_input, era_mappings)
        display_random_quote(quotes, search_message_handler, interpretation_message_handler, matched_era)
        
        continue_choice = input("Would you like another quote? (Y/N): ").lower()
        if continue_choice != 'y':
            print("Goodbye!")
            break
