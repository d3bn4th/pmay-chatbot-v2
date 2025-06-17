import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)
from langchain_core.documents import Document

def get_vector_collection() -> chromadb.Collection:
    """Get or create the vector collection for document storage."""
    ollama_ef = OllamaEmbeddingFunction(
        url="http://localhost:11434/api/embeddings",
        model_name="nomic-embed-text:latest",
    )
    chroma_client = chromadb.PersistentClient(path="./demo-rag-chroma")
    return chroma_client.get_or_create_collection(
        name="rag_app",
        embedding_function=ollama_ef,
        metadata={"hnsw:space": "cosine"},
    )

def query_collection(prompt: str, n_results: int = 20):
    """Query the vector collection for relevant documents."""
    try:
        collection = get_vector_collection()
        results = collection.query(
            query_texts=[prompt],
            n_results=n_results,
            include=["documents", "metadatas"]
        )
        
        # Debug print
        # print("Raw ChromaDB results:", results)
        
        # Extract and flatten the documents list
        if results and "documents" in results and results["documents"]:
            # ChromaDB returns documents as a list of lists, we want just the first list
            documents = results["documents"][0]
            metadatas = results["metadatas"][0] if "metadatas" in results and results["metadatas"] else []
            # Filter out any None or empty documents and ensure they are strings
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