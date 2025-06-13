import os
import tempfile
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def process_document(file_content: bytes, filename: str) -> list[Document]:
    """Process a document and split it into chunks."""
    if filename.lower().endswith(".pdf"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name

        loader = PyMuPDFLoader(tmp_file_path)
        documents = loader.load()

        os.unlink(tmp_file_path)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500, chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)
        return splits
    return [] 