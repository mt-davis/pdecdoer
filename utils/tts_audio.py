import requests
import streamlit as st

def generate_audio_from_text(text, api_key, voice_id=None, use_ssml=False):
    """Generate audio from text using ElevenLabs API
    
    Args:
        text (str): Text to convert to speech
        api_key (str): ElevenLabs API key
        voice_id (str, optional): Voice ID to use. Defaults to the standard voice if None.
        use_ssml (bool, optional): Whether the text is SSML formatted. Defaults to False.
        
    Returns:
        bytes: Audio data if successful, None if failed
    """
    # Log for debugging (will appear in server console)
    api_key_snippet = api_key[:4] + "..." + api_key[-4:] if api_key and len(api_key) > 8 else "[empty]"
    print(f"Generating audio with API key starting with {api_key_snippet}")
    
    # Validate API key
    if not api_key:
        st.error("No ElevenLabs API key provided. Please add your API key in the Settings page.")
        return None
    
    # If no voice_id is provided, try to get available voices first
    if not voice_id:
        try:
            # Get available voices
            voices_url = "https://api.elevenlabs.io/v1/voices"
            voices_headers = {"xi-api-key": api_key}
            voices_response = requests.get(voices_url, headers=voices_headers)
            
            if voices_response.status_code == 200:
                voices_data = voices_response.json()
                available_voices = voices_data.get("voices", [])
                
                if available_voices:
                    # Use the first available voice
                    effective_voice_id = available_voices[0]["voice_id"]
                    print(f"Using first available voice: {effective_voice_id}")
                else:
                    st.warning("No voices found in your ElevenLabs account. Using fallback voice.")
                    effective_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice, commonly available
            else:
                # Fallback to a common voice ID
                effective_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice, commonly available
        except Exception as e:
            print(f"Error getting voices: {str(e)}")
            effective_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice, commonly available
    else:
        effective_voice_id = voice_id
    
    print(f"Using voice ID: {effective_voice_id}")
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{effective_voice_id}"
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
    
    # Set appropriate settings for SSML
    if use_ssml:
        print("Using SSML for text-to-speech")
        payload["model_id"] = "eleven_turbo_v2"  # Using a model that supports SSML
        payload["text_type"] = "ssml"  # Indicate that text is SSML formatted
    
    try:
        print(f"Sending request to ElevenLabs API with {len(text)} characters of text")
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print("Successfully generated audio")
            return response.content
        else:
            # Handle specific error codes
            if response.status_code == 401:
                st.error("Authentication failed. Your ElevenLabs API key appears to be invalid.")
            elif response.status_code == 429:
                st.error("Rate limit exceeded. Your ElevenLabs plan may have usage restrictions.")
            else:
                error_msg = f"Error from ElevenLabs API: {response.status_code}"
                try:
                    error_data = response.json()
                    if "detail" in error_data:
                        error_msg += f" - {error_data['detail']}"
                    elif isinstance(error_data, dict) and "message" in error_data:
                        error_msg += f" - {error_data['message']}"
                except:
                    pass
                st.error(error_msg)
            
            print(f"ElevenLabs API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"TTS Error: {str(e)}")
        st.error(f"Error connecting to ElevenLabs API: {str(e)}")
        return None
