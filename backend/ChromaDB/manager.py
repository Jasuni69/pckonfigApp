from ChromaDB.client import get_chroma_client

# Initialize the Chroma client and get the collection
client = get_chroma_client()
collection = client.get_or_create_collection(name="components")

def add_component(doc: str, metadata: dict, id: str):
    """
    Add a single component to the Chroma collection.
    
    Args:
        doc (str): Natural language description of the component.
        metadata (dict): Structured data (e.g., {"type": "GPU", "price": 300}).
        id (str): Unique ID for this component.
    """
    collection.add(
        documents=[doc],
        metadatas=[metadata],
        ids=[id]
    )

def search_components(query: str, n_results: int = 3):
    """
    Search the collection for components similar to the query.

    Args:
        query (str): The search text (e.g., "budget GPU for 1440p gaming").
        n_results (int): How many results to return.

    Returns:
        dict: Chroma result with IDs, distances, documents, and metadatas.
    """
    return collection.query(
        query_texts=[query],
        n_results=n_results
    )