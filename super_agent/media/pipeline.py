from typing import Optional, Dict
from super_agent.brain.openai_brain import OpenAIBrain
from super_agent.voice.elevenlabs_tts import ElevenLabsTTS
from super_agent.avatar.did_avatar import DIDAvatar


class MediaPipeline:
    def __init__(
        self,
        openai_model: str = "gpt-4.1-mini",
        enable_voice: bool = False,
        enable_avatar: bool = False,
        elevenlabs_voice_id: Optional[str] = None,
        did_avatar_id: Optional[str] = None,
    ):
        self.brain = OpenAIBrain(model=openai_model)

        self.enable_voice = enable_voice
        self.enable_avatar = enable_avatar

        self.voice = (
            ElevenLabsTTS(voice_id=elevenlabs_voice_id)
            if enable_voice and elevenlabs_voice_id
            else None
        )

        self.avatar = (
            DIDAvatar(avatar_id=did_avatar_id)
            if enable_avatar and did_avatar_id
            else None
        )

    def run(self, user_text: str) -> Dict:
        # Step 1: Get AI response text
        response_text = self.brain.reply([{"role": "user", "content": user_text}])

        result = {
            "text": response_text,
            "audio_path": None,
            "video_url": None,
        }

        # Step 2: Generate voice (optional)
        if self.voice:
            audio_path = self.voice.synthesize(response_text)
            result["audio_path"] = audio_path
        else:
            audio_path = None

        # Step 3: Generate avatar video (optional)
        if self.avatar:
            video = self.avatar.create_video(
                text=response_text,
                audio_path=audio_path
            )
            result["video_url"] = video.get("video_url")

        return result
