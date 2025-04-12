import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(
    page_title="Policy Decoder App",
    page_icon="🧠",
    layout="wide"
)

st.markdown("""
    <style>
        .main-title {
            font-size: 2.8rem;
            font-weight: bold;
            color: #4B6A9B;
            text-align: center;
        }
        .subtext {
            font-size: 1.2rem;
            text-align: center;
            color: #5c5c5c;
            margin-bottom: 30px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🧠 Welcome to Policy Decoder</div>", unsafe_allow_html=True)
st.markdown("<div class='subtext'>An AI-powered civic education platform to explore, compare, and understand policies.</div>", unsafe_allow_html=True)

st.markdown("---")

st.markdown("### Explore Features from the Sidebar:")
st.markdown("""
- 📄 **Decoder**: Upload a bill and ask questions
- 🔍 **Compare Bills**: See side-by-side analysis of two policies
- 💬 **Chat with Memory**: Continue the conversation with AI
- 📊 **Impact Simulator**: Visualize how a bill could affect your life
- 🧑‍⚖️ **Legislator Lookup**: Get info on sponsors and votes
- 🔈 **Voice Summary**: Listen to simplified bill summaries
- 🎮 **Civic Quiz**: Test your knowledge on policy topics
- 📤 **Export Reports**: Save and share results as PDF
- ⚙️ **Settings**: Manage API keys, dark mode, and more
""")