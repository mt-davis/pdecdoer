from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_anthropic import ChatAnthropic

openai_llm = ChatOpenAI(openai_api_key=openai_api_key)
claude_llm = ChatAnthropic(anthropic_api_key=anthropic_api_key)

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
