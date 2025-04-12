import streamlit as st
import os
from dotenv import load_dotenv
from utils.session_tracker import track_activity
from components.ui_helpers import setup_page_config, sidebar_navigation, card, success_box

# Load environment variables
load_dotenv()

# Configure the page
st.set_page_config(
    page_title="Settings - PolicyCompassAI",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
from components.ui_helpers import apply_custom_css
apply_custom_css()

# With multipage apps, the sidebar navigation is handled automatically by Streamlit
# But we'll keep this for consistency with current app structure
sidebar_navigation()

# Header - simplified as page config already sets page title
st.markdown("<h1 class='page-title'>⚙️ App Settings</h1>", unsafe_allow_html=True)
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
st.markdown("<p class='subtext' style='text-align: center; margin-bottom: 2rem;'>Configure your API keys and preferences.</p>", unsafe_allow_html=True)

# API Keys section
card_content = """
<div>
    <h3>🔐 API Keys</h3>
    <p>Store your API keys for different services.</p>
</div>
"""
card(card_content)

# Initialize session state with values from .env if not already set
if "openai_key" not in st.session_state or not st.session_state.openai_key:
    st.session_state.openai_key = os.getenv("OPENAI_API_KEY", "")
if "anthropic_key" not in st.session_state or not st.session_state.anthropic_key:
    st.session_state.anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
if "propublica_key" not in st.session_state or not st.session_state.propublica_key:
    st.session_state.propublica_key = os.getenv("PROPUBLICA_API_KEY", "")
if "tts_key" not in st.session_state or not st.session_state.tts_key:
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY", "")
    st.session_state.tts_key = elevenlabs_key
    if elevenlabs_key:
        print(f"Loaded ElevenLabs API key from .env file (starts with {elevenlabs_key[:4]})")

col1, col2 = st.columns(2)

with col1:
    openai_key = st.text_input("OpenAI API Key", 
                               value=st.session_state.get("openai_key", ""), 
                               type="password",
                               key="openai")
    
    anthropic_key = st.text_input("Anthropic (Claude) API Key", 
                                  value=st.session_state.get("anthropic_key", ""), 
                                  type="password",
                                  key="anthropic")

with col2:
    propublica_key = st.text_input("ProPublica Congress API Key", 
                                  value=st.session_state.get("propublica_key", ""), 
                                  type="password",
                                  key="propublica")
    
    tts_key = st.text_input("TTS (ElevenLabs) API Key", 
                           value=st.session_state.get("tts_key", ""), 
                           type="password",
                           key="tts")

if st.button("Save All Keys", type="primary"):
    # Check which keys were updated
    updated_keys = []
    if openai_key != st.session_state.get("openai_key", ""):
        updated_keys.append("OpenAI")
    if anthropic_key != st.session_state.get("anthropic_key", ""):
        updated_keys.append("Anthropic")
    if propublica_key != st.session_state.get("propublica_key", ""):
        updated_keys.append("ProPublica")
    if tts_key != st.session_state.get("tts_key", ""):
        updated_keys.append("ElevenLabs")
    
    # Save all keys to session state
    st.session_state.openai_key = openai_key
    st.session_state.anthropic_key = anthropic_key
    st.session_state.propublica_key = propublica_key
    st.session_state.tts_key = tts_key
    
    # Track activity if any keys were updated
    if updated_keys:
        track_activity(
            action="updated API keys",
            page_name="Settings",
            details={
                "updated_keys": ", ".join(updated_keys)
            }
        )
    
    success_box("All API keys have been saved for this session")

# Show which keys are configured in .env file
st.markdown("### API Keys in Environment (.env)")
col1, col2 = st.columns(2)

with col1:
    openai_env = "✅" if os.getenv("OPENAI_API_KEY") else "❌"
    anthropic_env = "✅" if os.getenv("ANTHROPIC_API_KEY") else "❌"
    
    st.markdown(f"OpenAI API Key: {openai_env}")
    st.markdown(f"Anthropic API Key: {anthropic_env}")

with col2:
    propublica_env = "✅" if os.getenv("PROPUBLICA_API_KEY") else "❌"
    elevenlabs_env = "✅" if os.getenv("ELEVENLABS_API_KEY") else "❌"
    
    st.markdown(f"ProPublica API Key: {propublica_env}")
    st.markdown(f"ElevenLabs API Key: {elevenlabs_env}")

st.info("Keys configured in the .env file will be used as fallbacks if no key is provided in the session.")

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# Theme Preferences
card_content = """
<div>
    <h3>🌙 Theme Preferences</h3>
    <p>Customize the appearance of the app.</p>
</div>
"""
card(card_content)

theme = st.radio("Choose theme:", ["Light", "Dark", "System Default"], index=2)
if st.button("Apply Theme", disabled=True):
    # This would be implemented with custom theming in a production app
    pass

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# Mobile Features
card_content = """
<div>
    <h3>📱 Mobile App Features</h3>
    <p>Configure Progressive Web App (PWA) support.</p>
</div>
"""
card(card_content)

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

st.info("To enable PWA functionality, include this manifest in your deployment using a custom component or deployment hook.")

# Add a footer
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
