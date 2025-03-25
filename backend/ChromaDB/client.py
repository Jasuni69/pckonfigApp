import chromadb
from chromadb.config import Settings

# Create and return a Chroma client with persistent storage
def get_chroma_client(persist_directory: str = "./chroma_data") -> chromadb.Client:
    return chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=persist_directory
    ))