from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Initialize models with API keys from environment
openai_llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY)
claude_llm = ChatAnthropic(api_key=ANTHROPIC_API_KEY, model_name="claude-3-sonnet-20240229")

import json

def generate_quiz(context, openai_api_key):
    llm = ChatOpenAI(temperature=0.5, openai_api_key=openai_api_key)

    prompt = PromptTemplate(
        input_variables=["text"],
        template="""
        Based on the following content, generate a multiple-choice quiz with 3 questions.
        Each question should have 3 options and indicate the correct answer.
        Return your response in valid JSON like:
        [
          {"question": "...", "options": ["A", "B", "C"], "answer": "B"},
          ...
        ]

        Content:
        {text}
        """
    )

    response = llm.predict(prompt.format(text=context))

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return None
