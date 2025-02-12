import random
import csv

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


def display_random_quote(quotes, era=None):
    filtered_quotes = [q for q in quotes if era is None or q["era"].lower() == era.lower()]
    if not filtered_quotes:
        print(f"No quotes found for era: {era}")
        return

    selected_quote = random.choice(filtered_quotes)
    print()  # Add empty line before quote
    print(f'"{selected_quote["quote"]}"\n- {selected_quote["author"]} ({selected_quote["era"]})')
    print()  # Add empty line after quote


if __name__ == "__main__":
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