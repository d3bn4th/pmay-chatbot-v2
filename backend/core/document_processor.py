import os
import tempfile
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging

# Add imports for semantic chunking
try:
    from langchain_experimental.text_splitter import SemanticChunker
    from langchain_community.embeddings import OllamaEmbeddings
    SEMANTIC_CHUNKING_AVAILABLE = True
except ImportError:
    SEMANTIC_CHUNKING_AVAILABLE = False

logger = logging.getLogger(__name__)

def process_document(file_content: bytes, filename: str, chunking_method: str = "semantic") -> list[Document]:
    """Process a document and split it into chunks. Supports 'semantic' and 'character' chunking methods."""
    if filename.lower().endswith(".pdf"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name

        loader = PyMuPDFLoader(tmp_file_path)
        documents = loader.load()

        os.unlink(tmp_file_path)

        # Add filename as source metadata to each document
        for doc in documents:
            doc.metadata["source"] = filename

        # Try semantic chunking if requested and available
        if chunking_method == "semantic" and SEMANTIC_CHUNKING_AVAILABLE:
            try:
                embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
                text_splitter = SemanticChunker(embeddings)
                splits = text_splitter.split_documents(documents)
                return splits
            except Exception as e:
                logger.warning(f"Semantic chunking failed: {e}. Falling back to character-based chunking.")

        # Fallback: Character-based chunking
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000, chunk_overlap=1000
        )
        splits = text_splitter.split_documents(documents)
        return splits
    return [] 