import os
import requests
from typing import Optional, Dict


class DIDAvatar:
    def __init__(self):
        self.api_key = os.getenv("DID_API_KEY")
        if not self.api_key:
            raise RuntimeError("DID_API_KEY not found in environment.")

        self.base_url = "https://api.d-id.com"
        self.headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json",
        }

    def create_video(
        self,
        text: str,
        audio_path: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> Dict:
        """
        Creates a talking avatar video from text or audio.
        """

        try:
            payload = {
                "script": {
                    "type": "text",
                    "input": text,
                },
                "source_url": image_url or "https://create-images-results.d-id.com/default-avatar.png",
            }

            response = requests.post(
                f"{self.base_url}/talks",
                headers=self.headers,
                json=payload,
            )

            response.raise_for_status()

            data = response.json()

            return {
                "success": True,
                "id": data.get("id"),
                "video_url": data.get("result_url"),
                "raw_response": data,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
