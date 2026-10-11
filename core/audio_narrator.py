import os
import requests
from typing import Optional

class TrailAudioNarrator:
    """
    Hands-free trail audio alerts.
    If ELEVENLABS_API_KEY is configured, generates dynamic neural whisper voice.
    Otherwise, returns formatted speech synthesis text for client-side offline audio.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        # ElevenLabs 'Adam' or 'Brian' - deep, calm outdoor documentary voice
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

    def generate_narration(self, prediction_result: dict, output_path: str = "static/audio/latest_alert.mp3") -> dict:
        risk = prediction_result.get("risk_percent", 0)
        severity = prediction_result.get("severity", "ADVISORY")
        action = prediction_result.get("action", "")
        drop = prediction_result.get("telemetry", {}).get("pressure_drop", 0.0)

        # Crisp, outdoor trail script (5-8 seconds max)
        if risk >= 75:
            speech_text = f"Warning: Squall risk {risk} percent. Barometric pressure fell {drop} hectopascals. {action}"
        elif risk >= 45:
            speech_text = f"Trail advisory: Storm watch at {risk} percent. {action}"
        else:
            speech_text = f"Trail scan complete. Conditions stable at {risk} percent risk. Enjoy your hike."

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        audio_url = None
        has_elevenlabs = False

        if self.api_key:
            try:
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
                headers = {
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": self.api_key
                }
                payload = {
                    "text": speech_text,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {
                        "stability": 0.65,
                        "similarity_boost": 0.80
                    }
                }
                resp = requests.post(url, json=payload, headers=headers, timeout=10)
                if resp.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(resp.content)
                    audio_url = f"/{output_path}"
                    has_elevenlabs = True
            except Exception as e:
                print(f"ElevenLabs generation fallback: {e}")

        return {
            "speech_text": speech_text,
            "has_elevenlabs": has_elevenlabs,
            "audio_url": audio_url
        }
