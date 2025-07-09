import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import OllamaEmbeddingFunction
import os

# Path to the persistent ChromaDB directory (should match your app config)
PERSIST_PATH = os.path.join(os.path.dirname(__file__), '..', 'demo-rag-chroma')
COLLECTION_NAME = "rag_app"

# Initialize ChromaDB client
client = chromadb.PersistentClient(path=PERSIST_PATH)

# Try to get the collection
try:
    collection = client.get_collection(COLLECTION_NAME)
    # Get all IDs in the collection
    all_ids = collection.get(include=[], limit=None)["ids"]
    if all_ids:
        collection.delete(ids=all_ids)
        print(f"Deleted {len(all_ids)} embeddings from collection '{COLLECTION_NAME}'.")
    else:
        print(f"Collection '{COLLECTION_NAME}' is already empty.")
except Exception as e:
    print(f"Collection '{COLLECTION_NAME}' not found or error occurred: {e}. Attempting to create a new collection.")
    # If collection does not exist, create it
    ef = OllamaEmbeddingFunction(
        url="http://localhost:11434/api/embeddings",
        model_name="nomic-embed-text:latest",
    )
    client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    print(f"Created new collection '{COLLECTION_NAME}'.")

print("Vector DB embeddings cleared.") 