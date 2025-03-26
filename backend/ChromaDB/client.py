import chromadb
import os

# Create and return a Chroma client with persistent storage
def get_chroma_client(persist_directory: str = "./chroma_data"):
    """Create and return a Chroma client with persistent storage"""
    try:
        # Try connecting to the ChromaDB service first (for Docker)
        return chromadb.HttpClient(host="chromadb", port=8000)
    except Exception as e:
        print(f"Could not connect to ChromaDB service: {e}")
        print("Falling back to local client")
        # Fallback to local client
        return chromadb.PersistentClient(path=persist_directory)