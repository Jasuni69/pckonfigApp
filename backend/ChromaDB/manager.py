from ChromaDB.client import get_chroma_client
import random
from typing import Dict, List, Optional, Set

# Global variables for lazy initialization
_client = None
_collection = None

def get_client():
    """Get ChromaDB client with lazy initialization."""
    global _client
    if _client is None:
        try:
            _client = get_chroma_client()
        except Exception as e:
            print(f"Warning: ChromaDB client initialization failed: {e}")
            _client = None
    return _client

def get_collection():
    """Get ChromaDB collection with lazy initialization."""
    global _collection
    if _collection is None:
        client = get_client()
        if client is not None:
            try:
                _collection = client.get_or_create_collection(name="components")
            except Exception as e:
                print(f"Warning: ChromaDB collection initialization failed: {e}")
                _collection = None
    return _collection

def add_component(doc: str, metadata: dict, id: str):
    """
    Add a single component to the Chroma collection.
    
    Args:
        doc (str): Natural language description of the component.
        metadata (dict): Structured data (e.g., {"type": "GPU", "price": 300}).
        id (str): Unique ID for this component.
    """
    collection = get_collection()
    if collection is None:
        raise Exception("ChromaDB collection not available")
    
    collection.add(
        documents=[doc],
        metadatas=[metadata],
        ids=[id]
    )

def search_components(
    query: str, 
    n_results: int = 3, 
    component_type: Optional[str] = None,
    exclude_ids: Optional[Set[str]] = None,
    price_range: Optional[tuple] = None,
    diversity_factor: float = 0.3
):
    """
    Search the collection for components similar to the query with diversity controls.

    Args:
        query (str): The search text (e.g., "budget GPU for 1440p gaming").
        n_results (int): How many results to return.
        component_type (str, optional): Filter by component type (e.g., "GPU").
        exclude_ids (Set[str], optional): Component IDs to exclude from results.
        price_range (tuple, optional): (min_price, max_price) range filter.
        diversity_factor (float): Controls result diversity (0.0-1.0, higher = more diverse).

    Returns:
        dict: Chroma result with IDs, distances, documents, and metadatas.
    """
    collection = get_collection()
    if collection is None:
        # Return empty results if ChromaDB is not available
        return {"ids": [[]], "distances": [[]], "documents": [[]], "metadatas": [[]]}
    
    # Build where clause for filtering
    where_clause = {}
    if component_type:
        where_clause["type"] = {"$eq": component_type}
    
    if price_range:
        min_price, max_price = price_range
        price_filter = {}
        if min_price is not None:
            price_filter["$gte"] = min_price
        if max_price is not None:
            price_filter["$lte"] = max_price
        if price_filter:
            where_clause["price"] = price_filter
    
    # Get more results than needed for diversity filtering
    search_multiplier = max(3, int(n_results * (1 + diversity_factor * 5)))
    
    # Perform the search
    search_args = {
        "query_texts": [query],
        "n_results": min(search_multiplier, 50)  # Cap at 50 to avoid too large results
    }
    
    if where_clause:
        search_args["where"] = where_clause
    
    try:
        results = collection.query(**search_args)
    except Exception as e:
        print(f"Warning: ChromaDB search failed: {e}")
        return {"ids": [[]], "distances": [[]], "documents": [[]], "metadatas": [[]]}
    
    # Apply diversity filtering and exclusions
    if results["ids"] and results["ids"][0]:
        filtered_results = apply_diversity_filter(
            results, 
            n_results, 
            exclude_ids or set(),
            diversity_factor
        )
        return filtered_results
    
    return results

def apply_diversity_filter(
    results: Dict, 
    n_results: int, 
    exclude_ids: Set[str], 
    diversity_factor: float
) -> Dict:
    """
    Apply diversity filtering to search results to prevent repetitive suggestions.
    """
    if not results["ids"] or not results["ids"][0]:
        return results
    
    ids = results["ids"][0]
    distances = results["distances"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    
    # Filter out excluded IDs
    filtered_items = []
    for i, id_ in enumerate(ids):
        if id_ not in exclude_ids:
            filtered_items.append({
                "id": id_,
                "distance": distances[i],
                "document": documents[i],
                "metadata": metadatas[i],
                "index": i
            })
    
    if not filtered_items:
        return {"ids": [[]], "distances": [[]], "documents": [[]], "metadatas": [[]]}
    
    # Apply diversity selection
    selected_items = select_diverse_components(filtered_items, n_results, diversity_factor)
    
    # Rebuild results structure
    return {
        "ids": [[item["id"] for item in selected_items]],
        "distances": [[item["distance"] for item in selected_items]],
        "documents": [[item["document"] for item in selected_items]],
        "metadatas": [[item["metadata"] for item in selected_items]]
    }

def select_diverse_components(
    items: List[Dict], 
    n_results: int, 
    diversity_factor: float
) -> List[Dict]:
    """
    Select diverse components based on price, brand, and performance characteristics.
    """
    if len(items) <= n_results:
        return items
    
    selected = []
    remaining = items.copy()
    
    # Always include the best match first
    best_match = min(remaining, key=lambda x: x["distance"])
    selected.append(best_match)
    remaining.remove(best_match)
    
    # Track selected characteristics for diversity
    selected_brands = {best_match["metadata"].get("brand", "")}
    selected_price_ranges = {get_price_range(best_match["metadata"].get("price", 0))}
    
    # Select remaining items with diversity consideration
    while len(selected) < n_results and remaining:
        # Score each remaining item for diversity
        scored_items = []
        for item in remaining:
            diversity_score = calculate_diversity_score(
                item, selected_brands, selected_price_ranges, diversity_factor
            )
            similarity_score = 1.0 - item["distance"]  # Convert distance to similarity
            
            # Combine similarity and diversity scores
            final_score = (1 - diversity_factor) * similarity_score + diversity_factor * diversity_score
            
            scored_items.append((final_score, item))
        
        # Select the highest scoring item
        best_item = max(scored_items, key=lambda x: x[0])[1]
        selected.append(best_item)
        remaining.remove(best_item)
        
        # Update diversity tracking
        selected_brands.add(best_item["metadata"].get("brand", ""))
        selected_price_ranges.add(get_price_range(best_item["metadata"].get("price", 0)))
    
    return selected

def calculate_diversity_score(
    item: Dict, 
    selected_brands: Set[str], 
    selected_price_ranges: Set[str], 
    diversity_factor: float
) -> float:
    """
    Calculate a diversity score for an item based on how different it is from selected items.
    """
    score = 0.0
    
    # Brand diversity
    brand = item["metadata"].get("brand", "")
    if brand not in selected_brands:
        score += 0.4
    
    # Price range diversity
    price_range = get_price_range(item["metadata"].get("price", 0))
    if price_range not in selected_price_ranges:
        score += 0.3
    
    # Add some randomness for variety
    score += random.random() * 0.3
    
    return score

def get_price_range(price: float) -> str:
    """
    Categorize price into ranges for diversity calculation.
    """
    if price < 1000:
        return "budget"
    elif price < 3000:
        return "mid-range"
    elif price < 6000:
        return "high-end"
    else:
        return "premium"

def search_components_by_type(
    component_type: str, 
    purpose: str, 
    n_results: int = 3,
    exclude_ids: Optional[Set[str]] = None,
    budget_range: Optional[tuple] = None
) -> Dict:
    """
    Search for components of a specific type optimized for a given purpose.
    
    Args:
        component_type (str): Type of component (e.g., "GPU", "CPU")
        purpose (str): Intended use case (e.g., "1440p gaming", "video editing")
        n_results (int): Number of results to return
        exclude_ids (Set[str], optional): Component IDs to exclude
        budget_range (tuple, optional): (min_price, max_price) budget constraints
    
    Returns:
        Dict: Search results with component recommendations
    """
    collection = get_collection()
    if collection is None:
        # Return empty results if ChromaDB is not available
        return {"ids": [[]], "distances": [[]], "documents": [[]], "metadatas": [[]]}
    
    # Build optimized query based on component type and purpose
    query = f"{component_type} for {purpose}"
    
    # Add type-specific optimization keywords
    if component_type.lower() == "gpu":
        if "gaming" in purpose.lower():
            if "4k" in purpose.lower():
                query += " high-end graphics 4K gaming ray tracing"
            elif "1440p" in purpose.lower():
                query += " high performance 1440p gaming"
            elif "1080p" in purpose.lower():
                query += " budget-friendly 1080p gaming"
        elif any(term in purpose.lower() for term in ["video editing", "rendering", "3d"]):
            query += " professional workstation VRAM"
    
    elif component_type.lower() == "cpu":
        if "gaming" in purpose.lower():
            query += " gaming processor high single-core performance"
        elif any(term in purpose.lower() for term in ["rendering", "video editing", "3d"]):
            query += " multi-core workstation processor"
        elif "programming" in purpose.lower():
            query += " development compilation multi-tasking"
    
    # Use the regular search function with optimized query
    return search_components(
        query=query,
        n_results=n_results,
        component_type=component_type,
        exclude_ids=exclude_ids,
        price_range=budget_range,
        diversity_factor=0.4  # Higher diversity for type-specific searches
    )