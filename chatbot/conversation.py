from chatbot.ollama_client import chat
from database.models import save_message

SYSTEM_PROMPT = """You are FaceChat, a friendly AI assistant at a reception desk.
You greet users by name if known, chat naturally, and are helpful and warm.
Keep responses concise and conversational."""

class ConversationManager:
    def __init__(self, session_id, user_name="there"):
        self.session_id = session_id
        self.user_name = user_name
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]

    def greet(self, is_known: bool, name: str = "") -> str:
        if is_known:
            msg = f"Say hello warmly to {name} who you recognise. Ask how they are doing today."
        else:
            msg = f"Greet a new visitor named {name} warmly for the first time."
        self.history.append({"role": "user", "content": msg})
        reply = chat(self.history)
        self.history.append({"role": "assistant", "content": reply})
        save_message(self.session_id, "assistant", reply)
        return reply

    def respond(self, user_input: str) -> str:
        self.history.append({"role": "user", "content": user_input})
        save_message(self.session_id, "user", user_input)
        reply = chat(self.history)
        self.history.append({"role": "assistant", "content": reply})
        save_message(self.session_id, "assistant", reply)
        return reply