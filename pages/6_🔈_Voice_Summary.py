import streamlit as st
from utils.tts_audio import generate_audio_from_text

st.set_page_config(page_title="Voice Summary", layout="wide")
st.title("🔈 Listen to Policy Summaries")

with st.sidebar:
    tts_api_key = st.text_input("TTS API Key (e.g., ElevenLabs)", type="password")
    voice_id = st.text_input("Voice ID (optional)")

text_input = st.text_area("Paste summary or policy excerpt to convert to speech:", height=200)
convert_btn = st.button("Generate Audio")

if convert_btn and tts_api_key and text_input:
    with st.spinner("Generating voice summary..."):
        audio_bytes = generate_audio_from_text(text_input, tts_api_key, voice_id)

        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")
        else:
            st.error("Failed to generate audio. Check your API key or input.")
else:
    st.info("Enter a summary and API key to create a voice version.")
