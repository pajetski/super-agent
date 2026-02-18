import os
import time
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()


class ElevenLabsTTS:
    """
    Minimal ElevenLabs Text-to-Speech client (REST).
    Generates an MP3 file and returns the output file path.
    """

    def __init__(self, voice_id: str, model_id: str = "eleven_multilingual_v2"):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise RuntimeError("ELEVENLABS_API_KEY is missing. Check your .env file.")

        self.voice_id = voice_id
        self.model_id = model_id

    def synthesize_to_file(self, text: str, out_path: str) -> str:
        """
        Core ElevenLabs call.
        Writes MP3 to out_path and returns the file path.
        """
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
                "similarity_boost": 0.8,
            },
        }

        r = requests.post(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()

        out_file.write_bytes(r.content)
        return str(out_file)

    def synthesize(self, text: str, out_path: Optional[str] = None) -> str:
        """
        Convenience wrapper used by MediaPipeline.
        Automatically generates a timestamped filename if not provided.
        """
        if out_path is None:
            Path("temp").mkdir(exist_ok=True)
            out_path = f"temp/reply_{int(time.time())}.mp3"

        return self.synthesize_to_file(text, out_path)
