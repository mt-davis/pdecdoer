import streamlit as st

st.set_page_config(page_title="App Settings", layout="wide")
st.title("⚙️ App Settings")

st.markdown("---")

st.subheader("🔐 API Keys")
st.text_input("OpenAI API Key", type="password", key="openai")
st.text_input("Anthropic (Claude) API Key", type="password", key="anthropic")
st.text_input("ProPublica Congress API Key", type="password", key="propublica")
st.text_input("TTS (ElevenLabs) API Key", type="password", key="tts")

st.markdown("---")

st.subheader("🌙 Theme Preferences")
st.radio("Choose theme:", ["Light", "Dark", "System Default"], index=2)

st.markdown("---")

st.subheader("📱 Mobile App Features")
st.markdown("To add Progressive Web App (PWA) support, configure the manifest and service worker.")
st.code("""
manifest.json
{
  "name": "Policy Decoder",
  "short_name": "Decoder",
  "start_url": ".",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#4B6A9B",
  "icons": [
    {
      "src": "/icon.png",
      "sizes": "192x192",
      "type": "image/png"
    }
  ]
}
""", language="json")

st.markdown("Include this manifest in your HTML head with a custom component or deployment hook.")
