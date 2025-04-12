import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Optional: safe Claude setup
claude_llm = None
if ANTHROPIC_API_KEY:
    try:
        from langchain_anthropic import ChatAnthropic
        claude_llm = ChatAnthropic(api_key=ANTHROPIC_API_KEY, model_name="claude-3-sonnet-20240229")
    except Exception as e:
        print("Claude setup failed:", e)


def build_qa_chain(documents, openai_api_key=OPENAI_API_KEY, eli5=False):
    # Check if we have any content in the documents
    if not documents or all(not doc.page_content.strip() for doc in documents):
        # Return a function that explains there's no content
        def no_content_answer(query):
            return "I couldn't extract any readable content from the document you provided. Please try uploading a different PDF or pasting the text directly."
        return no_content_answer
        
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    chunks = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectorstore = FAISS.from_documents(chunks, embeddings)

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.3, openai_api_key=openai_api_key)
    
    # Create custom prompt for better context understanding
    qa_prompt_template = """You are an expert policy analyst. You're analyzing a policy document and need to answer questions about it.
    
    Use the following context to answer the question:
    {context}

    Question: {query}
    
    If the context doesn't contain enough information to answer the question, base your answer on the provided context and be upfront about any limitations.
    """
    
    if eli5:
        qa_prompt_template += "\n\nExplain your answer as if you're speaking to a 5-year-old, using simple language and examples."
    
    prompt = PromptTemplate(
        template=qa_prompt_template, 
        input_variables=["context", "query"]
    )
    
    # Use chain_type="stuff" to make sure all retrieved documents are passed to the LLM
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm, 
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        chain_type="stuff",  # Use "stuff" to include all documents in the prompt
        return_source_documents=True,  # Include source documents in response
        chain_type_kwargs={"prompt": prompt}  # Use our custom prompt
    )

    # Create a wrapper function that uses invoke instead of run
    def get_answer(query):
        try:
            response = qa_chain.invoke({"query": query})
            
            # Extract the actual answer text - new LangChain returns a dict with 'result' key
            if isinstance(response, dict):
                # Get the result from the response
                if 'result' in response:
                    result = response['result']
                else:
                    # Fall back to checking other common keys
                    result = response.get('answer', str(response))
                    
                # If the result indicates lack of knowledge, supplement with document content
                if "don't have enough information" in result.lower() or "don't know" in result.lower() or "cannot determine" in result.lower():
                    # Provide a direct answer using the document content
                    doc_content = "\n\n".join([d.page_content for d in chunks[:3]])
                    context_msg = f"Here's what I found in the document:\n\n{doc_content[:1500]}"
                    return context_msg
                    
                return result
                
            return response
        except Exception as e:
            # If any error occurs, return the document content directly
            doc_content = "\n\n".join([d.page_content for d in chunks[:3]])
            return f"I encountered an error processing your request, but here's the document content:\n\n{doc_content[:1500]}"

    # Return the wrapper function
    return get_answer