import random

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
