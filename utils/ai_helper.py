from utils.openai_client import get_openai_client
from rich.console import Console

console = Console()

def get_ai_response(system_message, user_prompt, max_tokens=150, temperature=0.7):
    """
    Generates a response from the OpenAI API based on a system message and user prompt.
    Returns None if an error occurs.
    """
    try:
        client = get_openai_client()
        if not client:
            return None
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        console.print(f"[bold red]Error generating AI response: {e}[/bold red]")
        return None
