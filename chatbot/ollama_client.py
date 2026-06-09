import ollama
from config.settings import OLLAMA_MODEL

def chat(messages: list[dict]) -> str:
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=messages
    )
    return response['message']['content']