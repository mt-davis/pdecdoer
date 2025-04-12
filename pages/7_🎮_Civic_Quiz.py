import streamlit as st
from chains.quiz_chain import generate_quiz
from utils.session_tracker import track_activity
from components.ui_helpers import setup_page_config, sidebar_navigation, info_box, error_box, card

# Setup page with consistent styling
setup_page_config("🎮 Civic Quiz")
st.markdown("<p class='subtext' style='text-align: center; margin-bottom: 2rem;'>Test your understanding with interactive quizzes.</p>", unsafe_allow_html=True)
# Add sidebar navigation
sidebar_navigation()

# Get API key from session state
openai_api_key = st.session_state.get("openai_key", "")

# Main card
card_content = """
<div>
    <h3>Generate a Quiz</h3>
    <p>Paste policy content below to create an interactive quiz.</p>
</div>
"""
card(card_content)

quiz_context = st.text_area("Paste a bill summary or excerpt for quiz generation:", height=200)
generate_btn = st.button("Generate Quiz", type="primary")

if generate_btn and openai_api_key and quiz_context:
    with st.spinner("Creating your quiz..."):
        quiz = generate_quiz(quiz_context, openai_api_key)

        if quiz:
            # Track activity for session summary
            track_activity(
                action="generated quiz",
                page_name="Civic Quiz",
                details={
                    "questions": len(quiz),
                    "context_length": len(quiz_context)
                }
            )
            
            st.markdown("### Test Your Knowledge:")
            for i, item in enumerate(quiz):
                st.markdown(f"**Q{i+1}:** {item['question']}")
                selected = st.radio(
                    "Choose an answer:",
                    item['options'],
                    key=f"q{i}"
                )
                with st.expander("Show Answer"):
                    st.markdown(f"✅ **Correct Answer:** {item['answer']}")
        else:
            error_box("Quiz generation failed. Try again with different input.")
else:
    info_box("Paste a summary and press Generate Quiz to begin. Make sure your OpenAI API key is set in the Settings page.")

# Add a footer
st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
