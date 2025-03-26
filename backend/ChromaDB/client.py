import chromadb
import os

# Create and return a Chroma client with persistent storage
def get_chroma_client(persist_directory: str = "./chroma_data"):
    try:
        # Try connecting to the ChromaDB service in docker-compose
        return chromadb.HttpClient(host="chromadb", port=8000)
    except Exception:
        # Fallback to local development with persistent storage
        return chromadb.PersistentClient(path=persist_directory)