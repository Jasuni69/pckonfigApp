import json
import chromadb

def clean_metadata(metadata):
    """Remove None values and convert values to supported types, properly handling numeric fields"""
    cleaned = {}
    for k, v in metadata.items():
        if v is None:
            cleaned[k] = ""
        elif k in ["price", "capacity"] and (isinstance(v, (int, float)) or (isinstance(v, str) and v.replace('.', '', 1).isdigit())):
            # Convert price and capacity to float for proper numeric filtering
            try:
                cleaned[k] = float(v)
            except (ValueError, TypeError):
                cleaned[k] = str(v)
        else:
            cleaned[k] = str(v)
    return cleaned

def test_chroma_locally():
    # Create in-memory client (new format)
    client = chromadb.EphemeralClient()
    
    # Create test collection
    collection_name = "test_components"
    
    # Delete the collection if it exists (to ensure fresh data)
    try:
        client.delete_collection(collection_name)
        print("Deleted existing collection to ensure fresh data load")
    except ValueError:
        print("No existing collection found, will create new one")
    
    # Create a fresh collection
    collection = client.create_collection(name=collection_name)
    print("Created fresh collection for loading data")
    
    # Load your JSON data
    with open('ChromaDB/components/chroma_components_final_polished.json', 'r') as f:
        data = json.load(f)
    
    total_components = len(data['chroma_components'])
    print(f"Loaded JSON data with {total_components} components")
    
    # Track component types for verification
    component_types = {}
    socket_types = {}
    
    # Keep track of seen IDs to avoid duplicates
    seen_ids = set()
    skipped_count = 0
    
    # Process all components
    batch_docs = []
    batch_metadatas = []
    batch_ids = []
    
    for idx, component in enumerate(data['chroma_components']):
        original_id = component['id']
        
        # If ID already seen, make it unique by appending a unique suffix
        if original_id in seen_ids:
            new_id = f"{original_id}_unique_{idx}"
            print(f"Found duplicate ID: {original_id}, using {new_id} instead")
            component_id = new_id
        else:
            component_id = original_id
            seen_ids.add(original_id)
        
        # Track component types and socket types
        component_type = component['metadata']['type']
        component_types[component_type] = component_types.get(component_type, 0) + 1
        
        if component_type == 'Motherboard' and 'socket' in component['metadata']:
            socket = component['metadata']['socket']
            socket_types[socket] = socket_types.get(socket, 0) + 1
        
        # Prepare data
        cleaned_metadata = clean_metadata(component['metadata'])
        batch_docs.append(component['document'])
        batch_metadatas.append(cleaned_metadata)
        batch_ids.append(component_id)
    
    # Add all components at once
    print(f"Adding {len(batch_ids)} components to ChromaDB")
    collection.add(
        documents=batch_docs,
        metadatas=batch_metadatas,
        ids=batch_ids
    )
    
    print("\nComponent type distribution in JSON:")
    for comp_type, count in component_types.items():
        print(f"  {comp_type}: {count} components")
    
    print("\nMotherboard socket distribution in JSON:")
    for socket, count in socket_types.items():
        if 'AM5' in socket:
            print(f"  {socket}: {count} motherboards (AM5)")
        else:
            print(f"  {socket}: {count} motherboards")
    
    # Verify what's actually in the ChromaDB collection
    print("\nVerifying data in ChromaDB...")
    chroma_component_types = {}
    
    for comp_type in component_types.keys():
        results = collection.query(
            query_texts=[comp_type],
            where={"type": {"$eq": comp_type}},
            n_results=1000  # Set high to get all
        )
        count = len(results['ids'][0]) if results['ids'] and results['ids'][0] else 0
        chroma_component_types[comp_type] = count
        print(f"  {comp_type}: {count} components in ChromaDB")
    
    # Specifically check Socket AM5 motherboards
    am5_results = collection.query(
        query_texts=["Motherboard"],
        where={"$and": [
            {"type": {"$eq": "Motherboard"}},
            {"socket": {"$eq": "Socket AM5"}}
        ]},
        n_results=100
    )
    
    print(f"\nFound {len(am5_results['ids'][0])} Socket AM5 motherboards in ChromaDB")
    if am5_results['ids'][0]:
        print("Sample AM5 motherboards in ChromaDB:")
        for i, metadata in enumerate(am5_results['metadatas'][0][:5]):  # Show first 5
            print(f"  {i+1}. {metadata.get('name')} - Socket: {metadata['socket']}")
    
    # Update the test query to use "Socket AM5" if we found them
    socket_am5_count = len(am5_results['ids'][0]) if am5_results['ids'] and am5_results['ids'][0] else 0
    
    # Test queries with and without filters
    test_queries = [
        {
            "query": "GPU",
            "filters": {"$and": [
                {"type": {"$eq": "GPU"}},
                {"price": {"$lt": 5000}}
            ]}
        },
        {
            "query": "Fast storage for gaming",
            "filters": {
                "type": {"$eq": "Storage"}
            }
        }
    ]
    
    # Add the appropriate motherboard query based on what's actually in our DB
    if socket_am5_count > 0:
        test_queries.append({
            "query": "AM5 motherboard",
            "filters": {"$and": [
                {"type": {"$eq": "Motherboard"}},
                {"socket": {"$eq": "Socket AM5"}}
            ]}
        })
    else:
        test_queries.append({
            "query": "Socket 1851 motherboard",
            "filters": {"$and": [
                {"type": {"$eq": "Motherboard"}},
                {"socket": {"$eq": "1851"}}
            ]}
        })
    
    for test in test_queries:
        print(f"\n{'='*50}")
        print(f"Testing query: {test['query']}")
        if test['filters']:
            print(f"Filters: {test['filters']}")
        print(f"{'='*50}")
        
        query_args = {
            "query_texts": [test['query']],
            "n_results": 3
        }
        if test['filters']:
            query_args["where"] = test['filters']
            
        # Add a debug print to see what actual metadata values exist
        if test['query'] == "Budget friendly GPU under 5000kr":
            print("Debugging GPU price values:")
            debug_results = collection.query(
                query_texts=["GPU"],
                where={"type": {"$eq": "GPU"}},
                n_results=5
            )
            for i, metadata in enumerate(debug_results['metadatas'][0]):
                print(f"GPU {i+1} Price: '{metadata['price']}' (Type: {type(metadata['price']).__name__})")
        
        if test['query'] == "Socket 1851 motherboard":
            print("Debugging ALL Motherboard socket values:")
            all_motherboards = collection.query(
                query_texts=["Motherboard"],
                where={"type": {"$eq": "Motherboard"}},
                n_results=20  # Get more results to see variety
            )
            
            print(f"Found {len(all_motherboards['ids'][0])} motherboards total")
            
            socket_counts = {}
            for metadata in all_motherboards['metadatas'][0]:
                socket = metadata.get('socket', 'Unknown')
                socket_counts[socket] = socket_counts.get(socket, 0) + 1
            
            print("Socket distribution:")
            for socket, count in socket_counts.items():
                print(f"  {socket}: {count} motherboards")
            
            # Try exact AM5 socket query
            am5_results = collection.query(
                query_texts=["Socket AM5"],
                where={"$and": [
                    {"type": {"$eq": "Motherboard"}},
                    {"socket": {"$eq": "Socket AM5"}}
                ]},
                n_results=5
            )
            
            print(f"\nFound {len(am5_results['ids'][0])} motherboards with exact 'Socket AM5'")
            for i, metadata in enumerate(am5_results['metadatas'][0]):
                print(f"  {i+1}. {metadata.get('name')} - Socket: {metadata['socket']}")
        
        results = collection.query(**query_args)
        
        # Enhanced results printing
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            print(f"\nResult {i+1}:")
            print(f"Component: {metadata.get('name', metadata.get('brand', 'Unknown'))}")
            print(f"Type: {metadata['type']}")
            print(f"Price: {metadata['price']} kr")
            print(f"Description: {doc}")
            print(f"Similarity Score: {results['distances'][0][i]}")
            print('-' * 30)

if __name__ == "__main__":
    test_chroma_locally()