import streamlit as st
import os
import requests
from dotenv import load_dotenv
from utils.tts_audio import generate_audio_from_text
from utils.session_tracker import get_session_summary, get_policy_content_summary, clear_session_activities, initialize_session_tracker, track_activity
from components.ui_helpers import setup_page_config, sidebar_navigation, card, info_box, error_box, success_box, apply_custom_css

# Load environment variables
load_dotenv()

# Configure the page
st.set_page_config(
    page_title="Voice Summary - PolicyCompassAI",
    page_icon="🔈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
apply_custom_css()

# Function to test ElevenLabs API key
def test_elevenlabs_api_key(api_key):
    """Test if an ElevenLabs API key is valid"""
    if not api_key:
        return False, "No API key provided"
    
    try:
        # Simple API call to get voices (lightweight request)
        url = "https://api.elevenlabs.io/v1/voices"
        headers = {"xi-api-key": api_key}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            voices = response.json().get("voices", [])
            return True, f"API key is valid. Found {len(voices)} voices available."
        elif response.status_code == 401:
            return False, "Invalid API key. Authentication failed."
        else:
            return False, f"API error: {response.status_code}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

# Function to get available voices
def get_available_voices(api_key):
    """Get list of available voices from ElevenLabs"""
    if not api_key:
        return []
    
    try:
        url = "https://api.elevenlabs.io/v1/voices"
        headers = {"xi-api-key": api_key}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            voices_data = response.json().get("voices", [])
            return voices_data
        else:
            print(f"Failed to get voices: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error getting voices: {str(e)}")
        return []

# With multipage apps, the sidebar navigation is handled automatically by Streamlit
# But we'll keep this for consistency with current app structure
sidebar_navigation()

st.markdown("<h1 class='page-title'>🔈 Voice Summary</h1>", unsafe_allow_html=True)
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
st.markdown("<p class='subtext' style='text-align: center; margin-bottom: 2rem;'>Convert policy text to speech for easier consumption.</p>", unsafe_allow_html=True)

# Get API key directly from environment first (for debugging)
env_api_key = os.getenv("ELEVENLABS_API_KEY", "")

# Then get from session state with fallback to environment
tts_api_key = st.session_state.get("tts_key") or env_api_key

# Display API key information (masked)
if tts_api_key:
    masked_key = tts_api_key[:4] + "..." + tts_api_key[-4:] if len(tts_api_key) > 8 else "***"
    st.success(f"ElevenLabs API key found (starts with {tts_api_key[:4]})")
    
    # Add button to test the API key
    if st.button("Test API Key"):
        with st.spinner("Testing API key..."):
            is_valid, message = test_elevenlabs_api_key(tts_api_key)
            if is_valid:
                st.success(message)
            else:
                st.error(message)
else:
    st.warning("ElevenLabs API key not found. Please set it in Settings or check your .env file.")
    with st.expander("API Key Troubleshooting"):
        st.write("API Key from environment:", "✅ Present" if env_api_key else "❌ Missing")
        st.write("API Key from session:", "✅ Present" if st.session_state.get("tts_key") else "❌ Missing")
        
        if not env_api_key:
            st.write("Make sure your .env file contains a line like:")
            st.code("ELEVENLABS_API_KEY=your_api_key_here")
            
        if not st.session_state.get("tts_key") and not env_api_key:
            st.write("You can add an API key directly here for this session:")
            direct_key = st.text_input("ElevenLabs API Key:", type="password")
            if direct_key and st.button("Use this key"):
                st.session_state.tts_key = direct_key
                st.rerun()

# Create tabs for different summary types
tab1, tab2, tab3 = st.tabs(["Custom Text", "Session Summary", "Policy Summary"])

with tab1:
    st.subheader("Convert Custom Text to Speech")
    
    # Get available voices and create dropdown
    available_voices = get_available_voices(tts_api_key)
    
    if available_voices:
        # Create voice options
        voice_options = [("", "Auto-select Voice")] + [(v["voice_id"], v["name"]) for v in available_voices]
        voice_labels = [f"{name}" for _, name in voice_options]
        voice_ids = [id for id, _ in voice_options]
        
        # Voice dropdown
        selected_index = st.selectbox(
            "Select Voice:", 
            options=range(len(voice_options)),
            format_func=lambda i: voice_labels[i]
        )
        voice_id = voice_ids[selected_index]
    else:
        # Fallback to text input if can't get voices
        voice_id = st.text_input("Voice ID (optional)", key="custom_voice_id")
    
    text_input = st.text_area("Paste summary or policy excerpt to convert to speech:", height=200)
    convert_btn = st.button("Generate Audio", key="custom_audio_btn")
    
    if convert_btn and tts_api_key and text_input:
        with st.spinner("Generating voice summary..."):
            audio_bytes = generate_audio_from_text(text_input, tts_api_key, voice_id)
            
            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3")
                st.download_button(
                    label="Download Audio",
                    data=audio_bytes,
                    file_name="policy_summary.mp3",
                    mime="audio/mp3"
                )
            else:
                error_box("Failed to generate audio. Check your API key or input.")

with tab2:
    st.subheader("Your Session Summary")
    
    # Initialize session tracker
    initialize_session_tracker()
    
    # Add session fix button
    st.markdown("### Session State Tools")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Check & Fix Session"):
            # This helps force a session state refresh
            if "user_activities" not in st.session_state or not st.session_state.user_activities:
                # Add a test activity if the session is empty
                from datetime import datetime
                st.session_state.user_activities = [{
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "action": "initialized session",
                    "page": "Voice Summary",
                    "details": {"note": "Session data may have been lost between pages"}
                }]
                st.info("Session was empty. Added initialization record.")
            else:
                st.success(f"Session contains {len(st.session_state.user_activities)} activities.")
            st.rerun()
    with col2:
        if st.button("Add Test Activity"):
            from utils.session_tracker import track_activity
            track_activity(
                action="tested voice summary",
                page_name="Voice Summary",
                details={"test": True}
            )
            st.rerun()
    
    # Get the session summary
    session_summary = get_session_summary()
    
    # Display the session summary
    st.markdown("### Summary of Your Activities")
    st.text_area("Session activities:", value=session_summary, height=200, key="session_summary", disabled=True)
    
    # Debug section
    with st.expander("Debug Session State"):
        st.write("#### Raw Activity Data")
        if "user_activities" in st.session_state and st.session_state.user_activities:
            st.write(f"Number of activities tracked: {len(st.session_state.user_activities)}")
            
            # Show pages with activities
            pages = set(activity["page"] for activity in st.session_state.user_activities)
            st.write(f"Pages with tracked activities: {', '.join(pages)}")
            
            # Show activities table
            st.write("#### All Activities")
            activities_data = []
            for activity in st.session_state.user_activities:
                activities_data.append({
                    "Time": activity["timestamp"].split()[1],
                    "Page": activity["page"],
                    "Action": activity["action"],
                    "Details": str(activity["details"])
                })
            st.dataframe(activities_data)
        else:
            st.write("No activities have been tracked yet.")
    
    # Option to generate audio from session summary
    col1, col2 = st.columns([1, 1])
    with col1:
        # Get available voices for session tab too
        available_voices = get_available_voices(tts_api_key)
        
        if available_voices:
            # Create voice options
            voice_options = [("", "Auto-select Voice")] + [(v["voice_id"], v["name"]) for v in available_voices]
            voice_labels = [f"{name}" for _, name in voice_options]
            voice_ids = [id for id, _ in voice_options]
            
            # Voice dropdown
            selected_index = st.selectbox(
                "Select Voice:", 
                options=range(len(voice_options)),
                format_func=lambda i: voice_labels[i],
                key="session_voice_select"
            )
            voice_id_session = voice_ids[selected_index]
        else:
            # Fallback to text input if can't get voices
            voice_id_session = st.text_input("Voice ID (optional)", key="session_voice_id")
    
    with col2:
        clear_btn = st.button("Clear Session History")
        if clear_btn:
            clear_session_activities()
            st.rerun()
    
    session_audio_btn = st.button("Generate Audio from Session Summary", key="session_audio_btn")
    
    if session_audio_btn and tts_api_key:
        if "You haven't performed any actions" in session_summary:
            info_box("There are no activities to summarize yet. Use the app more to generate a summary.")
        else:
            with st.spinner("Generating voice summary of your session..."):
                audio_bytes = generate_audio_from_text(session_summary, tts_api_key, voice_id_session)
                
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
                    st.download_button(
                        label="Download Session Summary Audio",
                        data=audio_bytes,
                        file_name="session_summary.mp3",
                        mime="audio/mp3"
                    )
                else:
                    error_box("Failed to generate audio. Check your API key.")

with tab3:
    st.subheader("Policy Content Summary")
    
    # Get the policy content summary
    policy_summary = get_policy_content_summary()
    
    # Function to further clean and format text for TTS
    def clean_for_tts(text):
        # Replace any remaining special characters that might cause TTS issues
        cleaned = text.replace("#", "")
        cleaned = cleaned.replace("*", "")
        cleaned = cleaned.replace("-", " ")
        cleaned = cleaned.replace("|", "")
        
        # Handle file extensions and common technical terms that TTS struggles with
        cleaned = cleaned.replace(".pdf", " PDF ")
        cleaned = cleaned.replace(".txt", " text file ")
        cleaned = cleaned.replace(".docx", " document ")
        cleaned = cleaned.replace(".md", " markdown ")
        
        # Handle acronyms more explicitly
        import re
        
        # Find acronyms that weren't handled by expand_abbreviations
        # This pattern finds uppercase sequences followed by lowercase or punctuation
        pattern = r'\b[A-Z]{2,}(?=[^A-Z]|$)'
        
        def acronym_handler(match):
            # Get the matched acronym
            acronym = match.group(0)
            
            # Common acronyms to pronounce as words
            pronounce_as_words = ["NASA", "COVID", "AIDS", "NATO"]
            if acronym in pronounce_as_words:
                return acronym
            
            # For all other acronyms, add spaces to make TTS spell it out
            return " ".join(list(acronym))
            
        # Apply acronym handling
        cleaned = re.sub(pattern, acronym_handler, cleaned)
        
        # Add periods at the end of lines that don't have punctuation to improve TTS pacing
        lines = cleaned.split("\n")
        for i in range(len(lines)):
            line = lines[i].strip()
            if line and not line[-1] in ['.', '!', '?', ':', ';', ',']:
                lines[i] = line + "."
        
        # Remove any mention of document filenames or paths
        cleaned = "\n".join(lines)
        
        # Remove vs_ and other filename patterns
        cleaned = re.sub(r'[a-zA-Z0-9_-]+\.[a-zA-Z0-9]{2,4}', '', cleaned)
        
        return cleaned
    
    # Clean the summary for better TTS rendering
    tts_friendly_summary = clean_for_tts(policy_summary)
    
    # Display the policy summary
    st.markdown("### Summary of Policy Documents")
    st.text_area("Policy content summary:", value=tts_friendly_summary, height=300, key="policy_summary", disabled=True)
    
    # Add option to refine summary
    col1, col2 = st.columns([3, 1]) 
    with col1:
        refine_options = st.multiselect(
            "Focus summary on specific content types:",
            options=["document", "comparison", "impact", "analysis"],
            default=[]
        )
    with col2:
        use_ssml = st.checkbox("Use SSML", help="Speech Synthesis Markup Language helps improve voice quality")
    
    # Add advanced options
    with st.expander("Advanced Speech Options"):
        col1, col2 = st.columns(2)
        with col1:
            acronym_handling = st.radio(
                "Acronym Handling:",
                options=["Spell Out", "Pronounce As Words"],
                index=0,
                help="How to handle acronyms like ICHRA in the speech"
            )
            
            custom_acronyms = st.text_input(
                "Custom Acronyms to Spell Out:",
                placeholder="Enter comma-separated: ICHRA,QSEHRA,ACA",
                help="Add your own acronyms to be spelled out"
            )
        
        with col2:
            speaking_rate = st.slider(
                "Speaking Rate", 
                min_value=0.7, 
                max_value=1.3, 
                value=1.0, 
                step=0.1, 
                help="Adjust how fast the voice speaks (1.0 is normal speed)"
            )
            
            pitch = st.slider(
                "Voice Pitch", 
                min_value=-10, 
                max_value=10, 
                value=0, 
                step=1, 
                help="Adjust pitch of the voice"
            )
    
    # Function to further clean text based on user preferences
    def apply_user_preferences(text, acronym_handling, custom_acronyms=""):
        import re
        
        # Add custom acronyms to be spelled out if provided
        if custom_acronyms:
            acronym_list = [a.strip() for a in custom_acronyms.split(",")]
            
            for acronym in acronym_list:
                if acronym and len(acronym) > 1:
                    # Replace the acronym with spaced letters
                    if acronym_handling == "Spell Out":
                        text = re.sub(
                            r'\b' + re.escape(acronym) + r'\b', 
                            " ".join(list(acronym)), 
                            text
                        )
                    
                    # Replace (ACRONYM) pattern
                    text = re.sub(
                        r'\(' + re.escape(acronym) + r'\)', 
                        f"(acronym {' '.join(list(acronym))})" if acronym_handling == "Spell Out" else f"(acronym {acronym})",
                        text
                    )
        
        # Final clean up
        text = text.replace("acronym acronym", "acronym")
        return text
    
    if refine_options:
        st.info(f"Showing focused summary for: {', '.join(refine_options)}")
        # This would actually filter the summary based on selected types
        # For now it just displays the message
    
    # Option to generate audio from policy summary
    col1, col2 = st.columns([1, 1])
    with col1:
        # Get available voices for policy summary tab
        available_voices = get_available_voices(tts_api_key)
        
        if available_voices:
            # Create voice options
            voice_options = [("", "Auto-select Voice")] + [(v["voice_id"], v["name"]) for v in available_voices]
            voice_labels = [f"{name}" for _, name in voice_options]
            voice_ids = [id for id, _ in voice_options]
            
            # Voice dropdown
            selected_index = st.selectbox(
                "Select Voice:", 
                options=range(len(voice_options)),
                format_func=lambda i: voice_labels[i],
                key="policy_voice_select"
            )
            voice_id_policy = voice_ids[selected_index]
        else:
            # Fallback to text input if can't get voices
            voice_id_policy = st.text_input("Voice ID (optional)", key="policy_voice_id")
    
    with col2:
        # Remove the speaking rate slider since it's in Advanced Options now
        st.write("") # Spacer
        st.write("Use the Advanced Speech Options for fine-tuning")
    
    policy_audio_btn = st.button("Generate Audio from Policy Summary", key="policy_audio_btn")
    
    if policy_audio_btn and tts_api_key:
        if "No policy documents have been analyzed" in policy_summary:
            info_box("There are no policy documents to summarize yet. Analyze some documents first.")
        else:
            with st.spinner("Generating voice summary of policy content..."):
                # Prepare text for TTS
                tts_text = tts_friendly_summary
                
                # Apply user preferences for acronyms
                tts_text = apply_user_preferences(tts_text, acronym_handling, custom_acronyms)
                
                # Apply SSML formatting if selected
                if use_ssml:
                    # Format with SSML for better speech synthesis
                    # Replace Section with proper break but also handle acronyms
                    formatted_text = tts_text.replace("Section", "<break strength='strong'/>Section")
                    
                    # Add emphasis to important sections
                    formatted_text = formatted_text.replace("Summary:", "<emphasis level='moderate'>Summary:</emphasis>")
                    formatted_text = formatted_text.replace("Analysis and Recommendations:", "<emphasis level='moderate'>Analysis and Recommendations:</emphasis>")
                    formatted_text = formatted_text.replace("General Recommendations", "<emphasis level='strong'>General Recommendations</emphasis>")
                    
                    # Add proper pauses after periods for better pacing
                    formatted_text = formatted_text.replace(". ", ".<break time='300ms'/> ")
                    
                    ssml_text = f"""<speak>
                        <prosody rate="{speaking_rate}" pitch="{pitch}%">
                            {formatted_text}
                        </prosody>
                    </speak>"""
                    tts_text = ssml_text
                
                # Generate audio
                audio_bytes = generate_audio_from_text(tts_text, tts_api_key, voice_id_policy, use_ssml=use_ssml)
                
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
                    st.download_button(
                        label="Download Policy Summary Audio",
                        data=audio_bytes,
                        file_name="policy_summary.mp3",
                        mime="audio/mp3"
                    )
                    
                    # Track this activity
                    track_activity(
                        action="generated policy voice summary",
                        page_name="Voice Summary",
                        details={"summary_length": len(tts_friendly_summary)}
                    )
                else:
                    error_box("Failed to generate audio. Check your API key.")

# Add a footer
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: var(--text-muted); font-size: 0.8rem;'>Voice summaries powered by ElevenLabs API</p>", unsafe_allow_html=True)
