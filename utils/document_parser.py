from langchain_community.document_loaders import PyPDFLoader, PDFPlumberLoader
from langchain.schema import Document
import os

def load_and_split_document(file_path=None, raw_text=None, max_pages=20):
    """
    Load and split a document from a file path or raw text.
    
    Args:
        file_path: Path to the PDF file.
        raw_text: Raw text content.
        max_pages: Maximum number of pages to process from a PDF (to avoid token limits).
    
    Returns:
        List of Document objects.
    """
    if file_path:
        try:
            # Try first with PyPDFLoader
            print(f"Loading PDF: {file_path}")
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # If we got empty content, try with PDFPlumberLoader
            if not documents or all(not doc.page_content.strip() for doc in documents):
                print("PyPDFLoader returned empty content, trying PDFPlumberLoader")
                loader = PDFPlumberLoader(file_path)
                documents = loader.load()
            
            # Limit number of pages to avoid token limits
            if len(documents) > max_pages:
                print(f"PDF has {len(documents)} pages, limiting to first {max_pages} pages")
                documents = documents[:max_pages]
                # Add a note about truncation
                note = Document(page_content=f"[Note: This document was truncated to {max_pages} pages. The original has {len(documents)} pages.]")
                documents.append(note)
                
            return documents
        except Exception as e:
            print(f"Error loading PDF: {e}")
            # Return a document with error information
            return [Document(page_content=f"Error loading PDF: {e}")]
    elif raw_text:
        # For raw text, create a single document
        return [Document(page_content=raw_text)]
    else:
        return []
