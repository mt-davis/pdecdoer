import streamlit as st
from chains.quiz_chain import generate_quiz

st.set_page_config(page_title="Civic Quiz", layout="wide")
st.title("🎮 Civic Quiz Mode")

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", type="password")

quiz_context = st.text_area("Paste a bill summary or excerpt for quiz generation:", height=200)
generate_btn = st.button("Generate Quiz")

if generate_btn and openai_api_key and quiz_context:
    with st.spinner("Creating your quiz..."):
        quiz = generate_quiz(quiz_context, openai_api_key)

        if quiz:
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
            st.error("Quiz generation failed. Try again with different input.")
else:
    st.info("Paste a summary and press Generate Quiz to begin.")
