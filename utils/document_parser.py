from langchain.document_loaders import PyPDFLoader
from langchain.schema import Document

def load_and_split_document(file_path=None, raw_text=None):
    if file_path:
        loader = PyPDFLoader(file_path)
        return loader.load()
    elif raw_text:
        return [Document(page_content=raw_text)]
    else:
        return []
