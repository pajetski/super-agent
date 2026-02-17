import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class OpenAIBrain:
    def __init__(self, model="gpt-4.1-mini", system_prompt=None):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is missing. Check your .env file.")

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.system_prompt = system_prompt or "You are a helpful AI assistant."

    def reply(self, messages: list) -> str:
        full_messages = [
            {"role": "system", "content": self.system_prompt}
        ] + messages

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=full_messages,
        )

        return resp.choices[0].message.content or ""
