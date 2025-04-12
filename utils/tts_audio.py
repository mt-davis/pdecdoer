import requests

def generate_audio_from_text(text, api_key, voice_id=None):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id or 'default'}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.content
    except Exception as e:
        print("TTS Error:", e)
    return None
