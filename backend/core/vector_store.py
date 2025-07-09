import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)
from langchain_core.documents import Document
from cachetools import LRUCache, cached
import json

# Singleton ChromaDB client, embedding function, and collection
_chroma_client = chromadb.PersistentClient(path="./demo-rag-chroma")
_ollama_ef = OllamaEmbeddingFunction(
    url="http://localhost:11434/api/embeddings",
    model_name="nomic-embed-text:latest",
)
_vector_collection = _chroma_client.get_or_create_collection(
    name="rag_app",
    embedding_function=_ollama_ef,
    metadata={"hnsw:space": "cosine"},
)

# LRU cache for query results (tune maxsize as needed)
_query_cache = LRUCache(maxsize=128)

def _make_cache_key(*args, **kwargs):
    # Support both positional and keyword arguments
    # Extract arguments by name, using defaults if not provided
    prompt = kwargs.get('prompt') if 'prompt' in kwargs else args[0] if len(args) > 0 else ""
    n_results = kwargs.get('n_results') if 'n_results' in kwargs else args[1] if len(args) > 1 else 5
    filter_metadata = kwargs.get('filter_metadata') if 'filter_metadata' in kwargs else args[2] if len(args) > 2 else None
    filter_str = json.dumps(filter_metadata, sort_keys=True) if filter_metadata else ""
    return f"{prompt}|{n_results}|{filter_str}"

def get_vector_collection() -> chromadb.Collection:
    """Return the singleton vector collection for document storage."""
    return _vector_collection

@cached(_query_cache, key=_make_cache_key)
def query_collection(prompt: str, n_results: int = 5, filter_metadata: dict = None):
    """Query the vector collection for relevant documents, with optional metadata filtering."""
    try:
        collection = get_vector_collection()
        query_args = {
            "query_texts": [prompt],
            "n_results": n_results,
            "include": ["documents", "metadatas"]
        }
        if filter_metadata:
            query_args["where"] = filter_metadata

        results = collection.query(**query_args)
        # Extract and flatten the documents list
        if results and "documents" in results and results["documents"]:
            documents = results["documents"][0]
            metadatas = results["metadatas"][0] if "metadatas" in results and results["metadatas"] else []
            documents = [str(doc) for doc in documents if doc]
            print(f"Processed {len(documents)} documents")
            return {"documents": documents, "metadatas": metadatas}
        print("No documents found in results")
        return {"documents": [], "metadatas": []}
    except Exception as e:
        print(f"Error in query_collection: {str(e)}")
        return {"documents": [], "metadatas": []}

def add_to_vector_collection(splits: list[Document], collection_name: str) -> int:
    """Add document splits to the vector collection."""
    collection = get_vector_collection()
    collection.add(
        documents=[s.page_content for s in splits],
        metadatas=[s.metadata for s in splits],
        ids=[f"doc_{collection_name}_{i}" for i in range(len(splits))],
    )
    return len(splits)

def list_uploaded_documents() -> list:
    """Return a list of unique uploaded document sources (filenames) from the vector collection."""
    collection = get_vector_collection()
    # Retrieve all metadatas (limit=None gets all)
    results = collection.get(include=["metadatas"], limit=None)
    metadatas = results.get("metadatas", [])
    sources = set()
    for meta in metadatas:
        # Each meta is a dict, may have 'source' key
        if isinstance(meta, dict) and "source" in meta:
            sources.add(meta["source"])
    return list(sources) 