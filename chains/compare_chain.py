import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")


from langchain.chat_models import ChatOpenAI
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_anthropic import ChatAnthropic

openai_llm = ChatOpenAI(openai_api_key=openai_api_key)
claude_llm = ChatAnthropic(api_key=anthropic_api_key, model_name="claude-3-sonnet-20240229")


def compare_policies(docs1, docs2, openai_api_key):
    llm = ChatOpenAI(temperature=0.3, openai_api_key=openai_api_key)

    content1 = "\n".join([d.page_content for d in docs1])
    content2 = "\n".join([d.page_content for d in docs2])

    merged_docs = [{"page_content": f"BILL 1:\n{content1}"}, {"page_content": f"BILL 2:\n{content2}"}]

    prompt = PromptTemplate(
        input_variables=["text"],
        template="""
        You are a legislative analyst. Compare the two policy texts below and summarize:
        - Key similarities
        - Major differences
        - Potential impact

        {text}
        """
    )

    chain = StuffDocumentsChain(llm=llm, prompt=prompt)
    response = chain.invoke(merged_docs)
    # Extract the actual answer text if it's a dictionary
    if isinstance(response, dict) and 'text' in response:
        return response['text']
    return response
