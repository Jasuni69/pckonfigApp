import json
from ChromaDB.client import get_chroma_client
import os

def clean_metadata(metadata):
    """Convert metadata values to appropriate types for filtering"""
    cleaned = {}
    for k, v in metadata.items():
        if k in ['price', 'capacity'] and v is not None:
            # Try to convert to float, but handle errors
            try:
                cleaned[k] = float(v)
            except (ValueError, TypeError):
                cleaned[k] = str(v) if v is not None else ""
        else:
            cleaned[k] = str(v) if v is not None else ""
    return cleaned

def populate_chroma():
    # Use host 'chromadb' for Docker networking
    client = get_chroma_client(persist_directory="/chroma/chroma_data")
    collection = client.get_or_create_collection(name="components")
    
    # Check if collection already has data
    if collection.count() > 0:
        print(f"ChromaDB collection already has {collection.count()} items. Skipping population.")
        return

    try:
        # Find the JSON file
        json_path = 'ChromaDB/components/chroma_components_final_polished.json'
        if not os.path.exists(json_path):
            print(f"Warning: {json_path} not found, looking for alternatives...")
            # Try alternative locations
            for alt_path in ['ChromaDB/chroma_components_enhanced.json', 'app/ChromaDB/components/chroma_components_enhanced.json']:
                if os.path.exists(alt_path):
                    json_path = alt_path
                    print(f"Found alternative path: {json_path}")
                    break
        
        # Load your enhanced JSON data
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Add components to collection
        for component in data['chroma_components']:
            cleaned_metadata = clean_metadata(component['metadata'])
            collection.add(
                documents=[component['document']],
                metadatas=[cleaned_metadata],
                ids=[component['id']]
            )
        
        print(f"Successfully populated ChromaDB with {len(data['chroma_components'])} components")
    except Exception as e:
        print(f"Error populating ChromaDB: {str(e)}")

if __name__ == "__main__":
    populate_chroma()