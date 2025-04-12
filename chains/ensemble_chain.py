import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
import asyncio
import streamlit as st

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Initialize models - only actually create them when needed
def get_openai_llm(api_key=None):
    """Get OpenAI LLM with proper API key prioritization"""
    # Use provided API key, or get from session state, or fall back to env variable
    api_key = api_key or st.session_state.get("openai_key", OPENAI_API_KEY)
    return ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.3, openai_api_key=api_key)

def get_claude_llm(api_key=None):
    """Get Claude LLM with proper API key prioritization"""
    # Use provided API key, or get from session state, or fall back to env variable
    api_key = api_key or st.session_state.get("anthropic_key", ANTHROPIC_API_KEY)
    
    if not api_key:
        return None
        
    try:
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(api_key=api_key, model_name="claude-3-sonnet-20240229")
    except Exception as e:
        print(f"Claude setup failed: {e}")
        return None

def build_single_qa_chain(documents, llm, high_school_level=False):
    """Build a QA chain for a single LLM"""
    # Check if we have any content in the documents
    if not documents or all(not doc.page_content.strip() for doc in documents):
        def no_content_answer(query):
            return "I couldn't extract any readable content from the document you provided. Please try uploading a different PDF or pasting the text directly."
        return no_content_answer
        
    # Split documents into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    chunks = splitter.split_documents(documents)

    # Create vector database
    api_key = st.session_state.get("openai_key", OPENAI_API_KEY)
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    # Create custom prompt for better context understanding
    qa_prompt_template = """You are an expert policy analyst tasked with analyzing a policy document. Your goal is to provide clear, accurate, and helpful information based on the document content.

    Context from the document:
    {context}

    Question: {query}
    
    Instructions:
    1. Answer based ONLY on the information provided in the context
    2. If you can't fully answer the question, explain what you CAN answer and what information is missing
    3. Be specific about which parts of the document support your answer
    4. If the context is unclear or ambiguous, acknowledge this and explain the limitations
    5. Do not make assumptions beyond what's explicitly stated in the document
    
    Format your response with:
    - Main answer
    - Supporting evidence from the document
    - Any limitations or caveats
    """
    
    if high_school_level:
        qa_prompt_template += """

        Please explain at a high school level (grades 9-12):
        - Use clear, straightforward language appropriate for high school students
        - Define technical terms and policy jargon when they first appear
        - Use relevant real-world examples to illustrate complex concepts
        - Break down complex ideas into more manageable parts
        - Connect policy concepts to topics typically covered in high school civics/government classes
        - Maintain academic rigor while ensuring accessibility
        """
    
    prompt = PromptTemplate(
        template=qa_prompt_template, 
        input_variables=["context", "query"]
    )
    
    # Create the QA chain with improved retrieval
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm, 
        retriever=vectorstore.as_retriever(
            search_kwargs={
                "k": 5,
                "fetch_k": 8
            }
        ),
        chain_type="stuff",
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )

    def get_answer(query):
        try:
            # First try to get a direct answer
            response = qa_chain.invoke({"query": query})
            
            if isinstance(response, dict):
                result = response.get('result', response.get('answer', str(response)))
                
                # Check if the response indicates lack of information
                if any(phrase in result.lower() for phrase in [
                    "don't have enough information",
                    "don't know",
                    "cannot determine",
                    "not enough context",
                    "cannot find"
                ]):
                    # Get more context and try a focused approach
                    relevant_docs = vectorstore.similarity_search(
                        query,
                        k=4,
                        fetch_k=8
                    )
                    
                    context = "\n\n".join([doc.page_content for doc in relevant_docs])
                    focused_prompt = f"""Based on this specific question: "{query}"
                    
                    Here is the relevant context from the document:
                    {context}
                    
                    Please provide:
                    1. The most relevant information you can find that relates to the question
                    2. Specific quotes or references from the document that support your response
                    3. Clear explanation of what aspects of the question you can and cannot answer based on this context
                    4. Suggestions for more specific questions that might yield better answers
                    
                    {'''Please explain at a high school level:
                    - Use clear language suitable for grades 9-12
                    - Define any technical terms
                    - Use relevant examples to illustrate concepts
                    - Break down complex ideas into understandable parts''' if high_school_level else ''}
                    
                    Remember to stay focused on what's actually in the document rather than making assumptions."""
                    
                    focused_response = llm.predict(focused_prompt)
                    return focused_response
                
                return result
            
            return str(response)
            
        except Exception as e:
            # Enhanced error handling with more helpful response
            try:
                relevant_docs = vectorstore.similarity_search(query, k=3)
                error_context = "\n\n".join([doc.page_content for doc in relevant_docs])
                
                error_prompt = f"""I encountered an error while analyzing this document. 
                
                Question asked: "{query}"
                
                Relevant document context:
                {error_context[:1500]}
                
                Please:
                1. Identify the most relevant information from this context
                2. Explain what we can determine from the available content
                3. Suggest 2-3 more specific questions that might be more answerable
                4. Note any important limitations or missing information
                
                {'''Explain at a high school level:
                - Use clear language suitable for grades 9-12
                - Define technical terms when needed
                - Use examples to illustrate complex points''' if high_school_level else ''}
                """
                
                error_response = llm.predict(error_prompt)
                return error_response
                
            except Exception as nested_e:
                return f"""I apologize, but I encountered multiple errors while trying to analyze the document. 
                
                To get better results, you could try:
                1. Rephrasing your question to be more specific
                2. Breaking your question into smaller, focused parts
                3. Checking if the document content is properly formatted and readable
                4. Ensuring the document contains the information you're looking for
                
                Original question: "{query}"
                """

    return get_answer

def build_ensemble_qa_chain(documents, openai_api_key=None, anthropic_api_key=None, high_school_level=False, ensemble_with="openai"):
    """
    Build an ensemble QA chain that uses multiple models and combines their responses.
    """
    # Initialize the models
    openai_llm = get_openai_llm(openai_api_key)
    claude_llm = get_claude_llm(anthropic_api_key)
    
    # Build individual chains
    openai_chain = build_single_qa_chain(documents, openai_llm, high_school_level)
    
    # Only build Claude chain if API key is available
    claude_chain = None
    if claude_llm:
        claude_chain = build_single_qa_chain(documents, claude_llm, high_school_level)
    
    # Choose which model to use for ensemble synthesis
    ensemble_llm = openai_llm
    if ensemble_with == "claude" and claude_llm:
        ensemble_llm = claude_llm
    
    def ensemble_answer(query):
        try:
            # Get responses from both models
            responses = {}
            
            # Always get OpenAI response
            openai_response = openai_chain(query)
            responses["OpenAI"] = openai_response
            
            # Get Claude response if available
            claude_response = None
            if claude_chain:
                claude_response = claude_chain(query)
                responses["Claude"] = claude_response
            
            # If Claude isn't available, return only OpenAI response
            if not claude_response:
                return {
                    "openai_response": openai_response,
                    "claude_response": None,
                    "ensemble_response": openai_response,
                    "models_used": ["OpenAI"]
                }
            
            # Create a prompt to synthesize the responses
            ensemble_prompt = f"""As an expert policy analyst, you need to synthesize two AI analyses of a policy document.

            Question asked: "{query}"
            
            First Analysis (OpenAI):
            {openai_response}
            
            Second Analysis (Claude):
            {claude_response}
            
            Please provide a comprehensive synthesis that:
            
            1. Identifies the key points where both analyses agree
            2. Highlights any unique insights or differences between the analyses
            3. Notes any limitations, uncertainties, or areas where more information is needed
            4. Provides specific evidence and quotes from the analyses to support the synthesis
            5. If both analyses indicate uncertainty or lack of information, suggest more specific questions that might yield better results
            
            Format the response as follows:
            
            Points of agreement between the analyses:
            [List key agreements]
            
            Differences in interpretation or additional insights:
            [List differences and unique contributions]
            
            Comprehensive answer:
            [Provide a well-structured synthesis that combines the best insights from both analyses]
            
            {'''Please maintain a high school level explanation:
            - Use clear language suitable for grades 9-12
            - Define any technical terms or policy jargon
            - Use relevant examples to illustrate complex concepts
            - Break down complex ideas into understandable parts
            - Connect policy concepts to high school civics/government topics''' if high_school_level else ''}
            """
            
            try:
                ensemble_response = ensemble_llm.predict(ensemble_prompt)
                
                # Check if the ensemble response is too generic or error-like
                if any(phrase in ensemble_response.lower() for phrase in [
                    "i apologize",
                    "error occurred",
                    "cannot provide",
                    "unable to process"
                ]):
                    # Fall back to a simpler synthesis
                    fallback_prompt = f"""The question was: "{query}"
                    
                    Please combine these two analyses in a simple, direct way:
                    
                    Analysis 1:
                    {openai_response}
                    
                    Analysis 2:
                    {claude_response}
                    
                    Focus on the concrete information we can provide from these analyses.
                    
                    {'''Maintain a high school level explanation:
                    - Use clear language for grades 9-12
                    - Define technical terms
                    - Use examples when helpful''' if high_school_level else ''}"""
                    
                    ensemble_response = ensemble_llm.predict(fallback_prompt)
            
            except Exception as e:
                # If synthesis fails, provide a simple combination
                ensemble_response = f"""Here are the insights from multiple analyses:

                OpenAI Analysis:
                {openai_response}

                Claude Analysis:
                {claude_response}

                Note: These are the direct analyses from each model. Consider both perspectives when drawing conclusions."""
            
            return {
                "openai_response": openai_response,
                "claude_response": claude_response,
                "ensemble_response": ensemble_response,
                "models_used": ["OpenAI", "Claude"]
            }
            
        except Exception as e:
            # Handle any errors in the ensemble process
            error_message = f"""I encountered an error while trying to combine the analyses.

            Here are the individual responses I was able to gather:
            
            OpenAI Analysis:
            {responses.get("OpenAI", "Error retrieving OpenAI response")}
            
            Claude Analysis:
            {responses.get("Claude", "Error retrieving Claude response or Claude not available")}
            
            To get better results, you might want to:
            1. Try asking a more specific question
            2. Break down your question into smaller parts
            3. Check if the document contains the information you're looking for
            
            Original question: "{query}" """
            
            return {
                "openai_response": responses.get("OpenAI", "Error in OpenAI response"),
                "claude_response": responses.get("Claude", "Error in Claude response"),
                "ensemble_response": error_message,
                "models_used": list(responses.keys())
            }
    
    return ensemble_answer 