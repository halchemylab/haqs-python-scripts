import random
import csv
from dotenv import load_dotenv
import os
from openai import OpenAI

ERA_MAPPINGS = {
    'e': 'Eastern',
    'r': 'Roman',
    'a': 'Renaissance',
    'g': 'Greek'
}

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

    selected_quote = random.choice(filtered_quotes)
    print()  # Add empty line before quote
    print(f'"{selected_quote["quote"]}"\n- {selected_quote["author"]} ({selected_quote["era"]})')
    
    # Get and display AI explanation
    explanation = get_ai_explanation(selected_quote["quote"], selected_quote["author"])
    print("\nAI Explanation:")
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