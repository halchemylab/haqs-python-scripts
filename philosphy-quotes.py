import random
import csv


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
    era_input = input("Enter an era to filter by (Eastern, Roman, Renaissance, Greek) or press Enter for random: ")
    quotes = load_quotes()
    display_random_quote(quotes, era_input if era_input else None)