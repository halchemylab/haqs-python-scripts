from utils.openai_client import get_openai_client

def get_ai_response(system_message, user_prompt, max_tokens=150, temperature=0.7):
    """
    Generates a response from the OpenAI API based on a system message and user prompt.
    """
    try:
        client = get_openai_client()
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
        return f"Error generating AI response: {e}"
