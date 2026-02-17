import os
from pathlib import Path
from dotenv import load_dotenv
import requests

load_dotenv()

class ElevenLabsTTS:
    """
    Minimal ElevenLabs Text-to-Speech client (REST).
    Writes an .mp3 file and returns the output path.
    """
    def __init__(self, voice_id: str, model_id: str = "eleven_multilingual_v2"):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise RuntimeError("ELEVENLABS_API_KEY is missing. Check your .env file.")

        self.voice_id = voice_id
        self.model_id = model_id

    def synthesize_to_file(self, text: str, out_path: str) -> str:
        out_file = Path(out_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        payload = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": {
                "stability": 0.4,
                "similarity_boost": 0.8
            }
        }

        r = requests.post(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()

        out_file.write_bytes(r.content)
        return str(out_file)
