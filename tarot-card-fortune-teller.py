import random
import os
import openai
import time

# Set your OpenAI API key here or ensure it's set as the environment variable "OPENAI_API_KEY"
openai.api_key = os.getenv("OPENAI_API_KEY")

# List of tarot cards (using the 22 major arcana for simplicity)
tarot_cards = [
    "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
    "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit",
    "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance",
    "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World"
]

# List of 10 potential focus questions
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

# List of 10 progress-message pairs (interpreting, consulting)
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
# Create a mutable copy that we will draw from
progress_pairs = ORIGINAL_PROGRESS_PAIRS.copy()

def get_progress_pair():
    """Return a random progress pair and remove it from the global list.
       Reset the list when all pairs have been used."""
    global progress_pairs
    if not progress_pairs:
        progress_pairs = ORIGINAL_PROGRESS_PAIRS.copy()
    pair = random.choice(progress_pairs)
    progress_pairs.remove(pair)
    return pair

def get_reading(question, cards):
    """
    Call the OpenAI API to generate a tarot reading based on the selected question and drawn cards.
    """
    prompt = (
        f"I have drawn the following tarot cards: {', '.join(cards)}. "
        f"The focus question is: '{question}'. "
        "Please provide a fun, insightful, and easy-to-understand tarot reading that interprets these cards."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a tarot card reader that provides supportive, concise, and easy-to-understand readings."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        reading = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        reading = f"Error generating reading: {e}"
    return reading

def main():
    print("Welcome to the Terminal Tarot Reading App!")
    while True:
        # Randomly select 3 questions from the list of 10
        sample_questions = random.sample(questions, 3)
        print("\nPlease choose one of the following focuses:")
        for idx, q in enumerate(sample_questions, start=1):
            print(f"{idx}. {q}")
        print()  # Add empty line here
        user_choice = input("Enter the number of your choice (1-3): ").strip()
        if user_choice not in ["1", "2", "3"]:
            print("Invalid choice. Please select 1, 2, or 3.")
            continue
        selected_question = sample_questions[int(user_choice)-1]
        
        # Draw 3 random tarot cards with pauses between each card
        drawn_cards = random.sample(tarot_cards, 3)
        print("\nDrawing 3 cards...")
        for card in drawn_cards:
            print(f"- {card}")
            time.sleep(1)  # pause 1 second between each card
 
        time.sleep(2)
        
        # Pick a progress pair randomly (without repeating until all have been used)
        interpret_msg, consult_msg = get_progress_pair()
        print(interpret_msg)
        time.sleep(2)
        print(consult_msg)
        time.sleep(2)
        
        # Get the tarot reading from OpenAI
        reading = get_reading(selected_question, drawn_cards)
        print("\nYour Tarot Reading:")
        print(reading)
        
        # Ask if the user wants another reading
        again = input("\nWould you like another reading? (y/n): ").strip().lower()
        if again != 'y':
            print("Thank you for using the Terminal Tarot Reading App. Wishing you positive vibes!")
            break

if __name__ == "__main__":
    main()
