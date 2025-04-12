import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Optional: safe Claude setup
claude_llm = None
if ANTHROPIC_API_KEY:
    try:
        from langchain.chat_models import ChatAnthropic
        claude_llm = ChatAnthropic(anthropic_api_key=ANTHROPIC_API_KEY)
    except Exception as e:
        print("Claude setup failed:", e)


def build_qa_chain(documents, openai_api_key=OPENAI_API_KEY, eli5=False):
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    chunks = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectorstore = FAISS.from_documents(chunks, embeddings)

    prompt_suffix = " Explain like I'm 5." if eli5 else ""

    llm = ChatOpenAI(temperature=0.3, openai_api_key=openai_api_key)
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())

    def run_query(query):
        return qa_chain.run(query + prompt_suffix)

    qa_chain.run = run_query
    return qa_chain