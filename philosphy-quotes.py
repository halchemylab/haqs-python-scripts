import random
import csv
from dotenv import load_dotenv
import os
import time
from openai import OpenAI

ERA_MAPPINGS = {
    'e': 'Eastern',
    'r': 'Roman',
    'a': 'Renaissance',
    'g': 'Greek'
}

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

# Keep track of used messages
used_search_messages = []
used_interpretation_messages = []

def get_random_message(message_list, used_messages):
    """Get a random message and track usage"""
    if not message_list or len(used_messages) >= len(message_list):
        used_messages.clear()
    
    available_messages = [m for m in message_list if m not in used_messages]
    message = random.choice(available_messages)
    used_messages.append(message)
    return message

def match_era(user_input):
    if not user_input:
        return None
    user_input = user_input.lower()
    # Exact match in mappings
    if user_input in ERA_MAPPINGS:
        return ERA_MAPPINGS[user_input]
    # Full name match
    for full_name in ERA_MAPPINGS.values():
        if user_input == full_name.lower():
            return full_name
    return None

def load_quotes(filename="quotes.csv"):
    quotes = []
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            quotes.append(row)
    return quotes

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

def display_random_quote(quotes, era=None):
    filtered_quotes = [q for q in quotes if era is None or q["era"].lower() == era.lower()]
    if not filtered_quotes:
        print(f"No quotes found for era: {era}")
        return

    time.sleep(1)
    selected_quote = random.choice(filtered_quotes)
    
    # Display first progress message and wait
    print(f"\n{get_random_message(SEARCH_MESSAGES, used_search_messages)}")
    time.sleep(3)
    
    # Display the quote
    print(f'\n"{selected_quote["quote"]}"\n- {selected_quote["author"]} ({selected_quote["era"]})')
    time.sleep(4)
    
    # Display second progress messages and wait - get two different messages
    first_msg = get_random_message(INTERPRETATION_MESSAGES, used_interpretation_messages)
    second_msg = get_random_message(INTERPRETATION_MESSAGES, used_interpretation_messages)
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
    print("Quick inputs: 'e' (Eastern), 'r' (Roman), 'a' (Renaissance), 'g' (Greek)")
    quotes = load_quotes()
    
    while True:
        era_input = input("Enter era (or press Enter for random): ")
        matched_era = match_era(era_input)
        display_random_quote(quotes, matched_era)
        
        continue_choice = input("Would you like another quote? (Y/N): ").lower()
        if continue_choice != 'y':
            print("Goodbye!")
            break
