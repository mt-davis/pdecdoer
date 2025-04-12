import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores import FAISS
from langchain.memory import ChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def build_chat_chain(documents, openai_api_key=OPENAI_API_KEY, reading_level="High School (Ages 14-17)"):
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    chunks = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectorstore = FAISS.from_documents(chunks, embeddings)

    memory_key = "chat_history"
    memory = ConversationBufferMemory(memory_key=memory_key, return_messages=True)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.2, openai_api_key=openai_api_key)

    # Create reading level instructions based on the selected level
    reading_level_instructions = {
        "Elementary (Ages 6-10)": "Use very simple words and short sentences. Explain as if talking to a 6-10 year old child. Use everyday examples and avoid any complex terms. If you must use a complex term, explain it like you would to a young child.",
        
        "Middle School (Ages 11-13)": "Use straightforward language appropriate for middle school students (ages 11-13). Break down complex concepts into simpler parts and use relatable examples. Define any specialized terms you use.",
        
        "High School (Ages 14-17)": "Use language appropriate for high school students. You can introduce more specialized terms but explain them clearly. Use examples that would be relevant to teenagers and young adults.",
        
        "College": "Use language appropriate for college students. You can use more specialized vocabulary and complex sentence structures. Provide nuanced explanations that acknowledge the complexity of the topic.",
        
        "Professional": "Use precise, technical language appropriate for professionals in the field. You can use specialized terminology without extensive explanation. Focus on providing detailed, accurate information that acknowledges the full complexity of the subject."
    }
    
    # Create a custom prompt template that incorporates the reading level
    qa_prompt_template = f"""
    You are an expert in explaining policy documents. You need to answer questions about a policy document.
    
    {reading_level_instructions.get(reading_level, reading_level_instructions["High School (Ages 14-17)"])}
    
    Chat History: {{chat_history}}
    
    Context from the policy document: {{context}}
    
    Human: {{question}}
    
    AI Assistant:
    """
    
    qa_prompt = PromptTemplate(
        input_variables=["chat_history", "context", "question"],
        template=qa_prompt_template
    )
    
    # Create the conversational chain with our custom prompt
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": qa_prompt}
    )
    
    # Create a wrapper function to extract just the answer from the response
    def get_response(query):
        result = chain.invoke({"question": query})
        if isinstance(result, dict) and 'answer' in result:
            return result['answer']
        return str(result)
    
    return get_response
