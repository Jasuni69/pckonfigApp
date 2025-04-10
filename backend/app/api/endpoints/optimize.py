from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from core.deps import get_current_user
from schemas import OptimizationRequest, OptimizedBuildOut
from models import CPU, GPU, RAM, PSU, Case, Storage, Cooler, Motherboard
from ChromaDB.manager import search_components
from typing import List, Dict, Any, Optional, Tuple
import logging
import json
import openai
from datetime import datetime
import traceback
import sys
import re

router = APIRouter()
logger = logging.getLogger(__name__)

# Define the debug function at the module level
def debug_print_gpu_objects(gpu_components):
    print("\nDEBUG - All GPU objects:")
    for i, gpu in enumerate(gpu_components):
        print(f"GPU {i+1}: ID={gpu.get('id')}, Name={gpu.get('name')}, Memory={gpu.get('memory')}")

@router.post("/build", response_model=OptimizedBuildOut)
async def optimize_build(
    request: OptimizationRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        print("\n==== OPTIMIZE BUILD START ====\n")
        logger.info("Received optimization request for purpose: %s", request.purpose)
        
        # Get current timestamp for created_at and updated_at fields
        current_time = datetime.utcnow()
        
        # Get current component details
        current_components = {}
        
        # Extract CPU details
        if request.cpu_id:
            cpu = db.query(CPU).filter(CPU.id == request.cpu_id).first()
            if cpu:
                current_components["cpu"] = {
                    "id": cpu.id,
                    "name": cpu.name,
                    "socket": cpu.socket,
                    "cores": cpu.cores,
                    "price": cpu.price
                }
        
        # Extract GPU details
        if request.gpu_id:
            gpu = db.query(GPU).filter(GPU.id == request.gpu_id).first()
            if gpu:
                current_components["gpu"] = {
                    "id": gpu.id,
                    "name": gpu.name,
                    "memory": getattr(gpu, 'memory', None),
                    "recommended_wattage": getattr(gpu, 'recommended_wattage', None),
                    "price": gpu.price
                }
        
        # Extract Motherboard details
        if request.motherboard_id:
            mb = db.query(Motherboard).filter(Motherboard.id == request.motherboard_id).first()
            if mb:
                current_components["motherboard"] = {
                    "id": mb.id,
                    "name": mb.name,
                    "socket": mb.socket,
                    "form_factor": mb.form_factor,
                    "price": mb.price
                }
        
        # Extract RAM details
        if request.ram_id:
            ram = db.query(RAM).filter(RAM.id == request.ram_id).first()
            if ram:
                current_components["ram"] = {
                    "id": ram.id,
                    "name": ram.name,
                    "capacity": ram.capacity,
                    "speed": getattr(ram, 'speed', None),
                    "price": ram.price
                }
        
        # Extract PSU details
        if request.psu_id:
            psu = db.query(PSU).filter(PSU.id == request.psu_id).first()
            if psu:
                current_components["psu"] = {
                    "id": psu.id,
                    "name": psu.name,
                    "wattage": psu.wattage,
                    "price": psu.price
                }
        
        # Extract Case details
        if request.case_id:
            case = db.query(Case).filter(Case.id == request.case_id).first()
            if case:
                current_components["case"] = {
                    "id": case.id,
                    "name": case.name,
                    "form_factor": case.form_factor,
                    "price": case.price
                }
        
        # Extract Storage details
        if request.storage_id:
            storage = db.query(Storage).filter(Storage.id == request.storage_id).first()
            if storage:
                current_components["storage"] = {
                    "id": storage.id,
                    "name": storage.name,
                    "capacity": storage.capacity,
                    "price": storage.price
                }
        
        # Extract Cooler details
        if request.cooler_id:
            cooler = db.query(Cooler).filter(Cooler.id == request.cooler_id).first()
            if cooler:
                current_components["cooler"] = {
                    "id": cooler.id,
                    "name": cooler.name,
                    "price": cooler.price
                }

        logger.debug("Current components: %s", json.dumps(current_components, indent=2))
        
        # Define the purpose for component search
        purpose = request.purpose or "general use"
        
        # Function to extract and format component data from ChromaDB results
        def extract_components_from_results(results: Dict[str, Any], component_type: str, limit: int = 3) -> List[Dict[str, Any]]:
            components = []
            try:
                print(f"\n--- Extracting {component_type} from ChromaDB results ---")
                print(f"Result type: {type(results)}")
                
                if not results:
                    print(f"No results returned for {component_type}")
                    return components
                
                if not isinstance(results, dict):
                    print(f"Results for {component_type} is not a dictionary: {results}")
                    return components
                
                print(f"Result keys: {results.keys()}")
                
                if "metadatas" not in results or not results["metadatas"]:
                    print(f"No 'metadatas' found in {component_type} results")
                    return components
                
                if not results["metadatas"][0]:
                    print(f"'metadatas' list is empty for {component_type}")
                    return components
                
                print(f"First metadata item: {json.dumps(results['metadatas'][0][0], indent=2)}")
                
                # Check if there are any component types in the metadata
                types = set()
                for metadata_list in results["metadatas"]:
                    for metadata in metadata_list:
                        if "type" in metadata:
                            types.add(metadata["type"])
                
                print(f"Component types found in results: {types}")
                
                for i, metadata in enumerate(results["metadatas"][0]):
                    if i >= 3:  # Only process first few items to avoid log spam
                        print(f"... and {len(results['metadatas'][0]) - 3} more items (skipping details for brevity)")
                        break
                        
                    print(f"\nProcessing metadata {i} for {component_type}: {json.dumps(metadata, indent=2)}")
                    
                    try:
                        # Extract ID from metadata or ID string
                        component_id = None
                        metadata_type = metadata.get("type", "").lower()
                        
                        # Check if this is for the right component type
                        if metadata_type != component_type.lower():
                            print(f"Skipping: metadata type '{metadata_type}' doesn't match '{component_type.lower()}'")
                            continue
                        
                        if "id" in metadata:
                            component_id = metadata["id"]
                            if isinstance(component_id, str) and component_id.isdigit():
                                component_id = int(component_id)
                            print(f"Found ID in metadata: {component_id}")
                        
                        # If no ID in metadata, try to extract from ID string
                        if component_id is None and i < len(results["ids"][0]):
                            id_str = results["ids"][0][i]
                            print(f"Trying to extract ID from string: {id_str}")
                            
                            if "_" in id_str:
                                id_parts = id_str.split("_")
                                if len(id_parts) > 1 and id_parts[-1].isdigit():
                                    component_id = int(id_parts[-1])
                                    print(f"Extracted ID from string: {component_id}")
                            else:
                                print(f"ID string doesn't contain underscore: {id_str}")
                        
                        # Only add components with valid IDs
                        if component_id is not None:
                            component_data = {"id": component_id, "name": metadata.get("name", "Unknown")}
                            
                            # Add type-specific fields
                            if component_type.lower() == "cpu":
                                component_data.update({
                                    "socket": metadata.get("socket", "Unknown"),
                                    "cores": metadata.get("cores", 0),
                                    "price": metadata.get("price", 0)
                                })
                            elif component_type.lower() == "gpu":
                                component_data.update({
                                    "memory": metadata.get("memory", "Unknown"),
                                    "price": metadata.get("price", 0)
                                })
                            elif component_type.lower() == "motherboard":
                                component_data.update({
                                    "socket": metadata.get("socket", "Unknown"),
                                    "form_factor": metadata.get("form_factor", "Unknown"),
                                    "price": metadata.get("price", 0)
                                })
                            elif component_type.lower() == "ram":
                                component_data.update({
                                    "capacity": metadata.get("capacity", 0),
                                    "speed": metadata.get("speed", 0),
                                    "price": metadata.get("price", 0)
                                })
                            elif component_type.lower() == "psu":
                                component_data.update({
                                    "wattage": metadata.get("wattage", 0),
                                    "price": metadata.get("price", 0)
                                })
                            elif component_type.lower() == "case":
                                component_data.update({
                                    "form_factor": metadata.get("form_factor", "Unknown"),
                                    "price": metadata.get("price", 0)
                                })
                            elif component_type.lower() == "storage":
                                component_data.update({
                                    "capacity": metadata.get("capacity", 0),
                                    "price": metadata.get("price", 0)
                                })
                            elif component_type.lower() == "cooler":
                                component_data.update({
                                    "price": metadata.get("price", 0)
                                })
                            
                            components.append(component_data)
                            print(f"Added component: {json.dumps(component_data, indent=2)}")
                            
                            if len(components) >= limit:
                                break
                    except Exception as e:
                        print(f"Error processing {component_type} metadata {i}: {str(e)}")
                        print(traceback.format_exc())
                
                print(f"Extracted {len(components)} {component_type} components")
                return components
            except Exception as e:
                print(f"Error in extract_components_from_results for {component_type}: {str(e)}")
                print(traceback.format_exc())
                return components
        
        # Function to get database fallbacks if ChromaDB doesn't return enough results
        def get_db_fallbacks(model, component_type, existing_components, limit=3):
            try:
                needed = limit - len(existing_components)
                if needed <= 0:
                    return existing_components
                    
                # Get IDs of existing components to avoid duplicates
                existing_ids = [c["id"] for c in existing_components]
                
                # Query for additional components, excluding existing ones
                additional_components = []
                query = db.query(model)
                
                if existing_ids:
                    query = query.filter(~model.id.in_(existing_ids))
                
                db_components = query.order_by(model.price.desc()).limit(needed).all()
                
                for comp in db_components:
                    component_data = {"id": comp.id, "name": comp.name, "price": comp.price}
                    
                    # Add type-specific fields
                    if component_type.lower() == "cpu":
                        component_data.update({
                            "socket": comp.socket,
                            "cores": comp.cores
                        })
                    elif component_type.lower() == "gpu":
                        component_data.update({
                            "memory": getattr(comp, 'memory', None)
                        })
                    elif component_type.lower() == "motherboard":
                        component_data.update({
                            "socket": comp.socket,
                            "form_factor": comp.form_factor
                        })
                    elif component_type.lower() == "ram":
                        component_data.update({
                            "capacity": comp.capacity,
                            "speed": getattr(comp, 'speed', None)
                        })
                    elif component_type.lower() == "psu":
                        component_data.update({
                            "wattage": comp.wattage
                        })
                    elif component_type.lower() == "case":
                        component_data.update({
                            "form_factor": comp.form_factor
                        })
                    elif component_type.lower() == "storage":
                        component_data.update({
                            "capacity": comp.capacity
                        })
                    # No special fields for coolers
                    
                    additional_components.append(component_data)
                
                print(f"Added {len(additional_components)} fallback {component_type} components from database")
                return existing_components + additional_components
            except Exception as e:
                print(f"Error in get_db_fallbacks for {component_type}: {str(e)}")
                print(traceback.format_exc())
                return existing_components
        
        # Add this function after your existing extract_components_from_results function
        def filter_components_for_purpose(components, purpose, component_type, limit=3):
            """Filter and prioritize components based on purpose"""
            if not components or len(components) <= 1:
                return components
            
            purpose = purpose.lower()
            scored_components = []
            
            # Score boost for high-end components in 4K gaming
            if "4k" in purpose and "gaming" in purpose:
                for component in components:
                    score = 0
                    name = component.get("name", "").lower()
                    
                    # GPU scoring for 4K gaming
                    if component_type == "gpu":
                        # Prioritize high VRAM GPUs
                        memory_str = component.get("memory", "")
                        if isinstance(memory_str, str) and "gb" in memory_str.lower():
                            try:
                                memory_value = int(memory_str.lower().split("gb")[0].strip())
                                if memory_value >= 12:
                                    score += 30
                                elif memory_value >= 10:
                                    score += 20
                                elif memory_value >= 8:
                                    score += 10
                            except (ValueError, TypeError):
                                pass
                        
                        # Prioritize high-end GPU models
                        if any(gpu in name for gpu in ["rtx 4090", "rtx 4080", "rtx 4070 ti", "radeon 7900"]):
                            score += 40
                        elif any(gpu in name for gpu in ["rtx 4070", "rtx 3090", "rtx 3080", "radeon 7800"]):
                            score += 30
                        elif any(gpu in name for gpu in ["rtx 4060 ti", "rtx 3070", "radeon 6800"]):
                            score += 20
                    
                    # CPU scoring for 4K gaming
                    elif component_type == "cpu":
                        # Prioritize high core count CPUs
                        cores = component.get("cores", 0)
                        # Make sure cores is an integer
                        if not isinstance(cores, int):
                            try:
                                cores = int(cores)
                            except (ValueError, TypeError):
                                cores = 0
                        
                        if cores >= 12:
                            score += 30
                        elif cores >= 8:
                            score += 20
                        elif cores >= 6:
                            score += 10
                        
                        # Prioritize high-end CPU models
                        if any(cpu in name for cpu in ["i9", "ryzen 9", "7950", "7900", "13900", "14900"]):
                            score += 30
                        elif any(cpu in name for cpu in ["i7", "ryzen 7", "7800x3d", "13700", "14700"]):
                            score += 20
                        elif any(cpu in name for cpu in ["i5", "ryzen 5", "7600", "13600", "14600"]):
                            score += 10
                    
                    # RAM scoring for 4K gaming
                    elif component_type == "ram":
                        # Prioritize higher capacity
                        capacity = component.get("capacity", 0)
                        # Make sure capacity is a number
                        if not isinstance(capacity, (int, float)):
                            try:
                                capacity = float(capacity)
                            except (ValueError, TypeError):
                                capacity = 0
                        
                        if capacity >= 32:
                            score += 30
                        elif capacity >= 16:
                            score += 15
                        
                        # Prioritize DDR5 and faster RAM
                        if "ddr5" in name:
                            score += 20
                        
                        speed = component.get("speed", 0)
                        # Make sure speed is a number
                        if not isinstance(speed, (int, float)):
                            try:
                                speed = float(speed)
                            except (ValueError, TypeError):
                                speed = 0
                        
                        if speed >= 6000:
                            score += 20
                        elif speed >= 4800:
                            score += 15
                        elif speed >= 3600:
                            score += 10
                    
                    # Storage scoring for 4K gaming - prefer SSDs
                    elif component_type == "storage":
                        if any(s in name.lower() for s in ["ssd", "nvme", "m.2"]):
                            score += 40
                        
                        # Prioritize larger capacity
                        capacity = component.get("capacity", 0)
                        # Make sure capacity is a number
                        if not isinstance(capacity, (int, float)):
                            try:
                                capacity = float(capacity)
                            except (ValueError, TypeError):
                                capacity = 0
                        
                        if capacity >= 2:
                            score += 20
                        elif capacity >= 1:
                            score += 10
                    
                    # Add the base score (to maintain original ordering if scores are equal)
                    original_index = components.index(component)
                    base_score = len(components) - original_index
                    score += base_score
                    
                    scored_components.append((score, component))
            else:
                # For non-4K gaming, preserve original order but still convert to scored format
                for i, component in enumerate(components):
                    score = len(components) - i  # Higher score for earlier items
                    scored_components.append((score, component))
            
            # Sort by score (descending) and take top N
            scored_components.sort(reverse=True, key=lambda x: x[0])
            return [comp for score, comp in scored_components[:limit]]
        
        # First, add this validation function near the top of the file
        def extract_gb(memory_str):
            """Extract gigabyte value from memory strings like '12GB', '8 GB', etc."""
            if not memory_str or not isinstance(memory_str, str):
                return None
            
            match = re.search(r"(\d+(?:\.\d+)?)\s*gb", memory_str.lower())
            if match:
                return float(match.group(1))
            return None

        def validate_gpu_for_4k(gpu):
            """Check if GPU has sufficient VRAM for 4K gaming"""
            logger.debug("Validating GPU for 4K: %s", gpu)
            if not gpu:
                return False
            
            memory_value = extract_gb(gpu.get('memory', ''))
            logger.debug("Extracted GPU Memory: %s GB", memory_value)
            return memory_value is not None and memory_value >= 12
        
        # Prepare component recommendations using ChromaDB
        recommendations = {}
        max_components = 3  # Maximum number of components per type to include
        
        # CPU recommendations
        cpu_query = f"best CPU for {purpose}"
        print(f"\nSearching ChromaDB for: {cpu_query}")
        cpu_results = search_components(cpu_query, n_results=10)
        cpu_components = extract_components_from_results(cpu_results, "cpu", max_components)
        cpu_components = filter_components_for_purpose(cpu_components, purpose, "cpu", max_components)
        recommendations["cpus"] = get_db_fallbacks(CPU, "cpu", cpu_components, max_components)
        
        # GPU recommendations
        gpu_query = f"best GPU for {purpose}"
        print(f"\n=== GPU RECOMMENDATIONS DEBUG ===")
        print(f"Query: {gpu_query}")
        gpu_results = search_components(gpu_query, n_results=10)  # Increase n_results to see more options
        print(f"Raw ChromaDB results for GPU:")
        print(json.dumps(gpu_results, indent=2))

        gpu_components = extract_components_from_results(gpu_results, "gpu", max_components)
        print(f"Extracted GPU components:")
        print(json.dumps(gpu_components, indent=2))

        # After getting gpu_components, call the debug function
        gpu_components = filter_components_for_purpose(gpu_components, purpose, "gpu", max_components)
        recommendations["gpus"] = get_db_fallbacks(GPU, "gpu", gpu_components, max_components)
        debug_print_gpu_objects(recommendations["gpus"])  # Add the debug call here
        print(f"Final GPU recommendations (with fallbacks):")
        print(json.dumps(recommendations["gpus"], indent=2))
        print(f"=== END GPU DEBUG ===\n")
        
        # Motherboard recommendations
        mb_query = f"compatible motherboard for {purpose}"
        if 'cpu' in current_components:
            mb_query += f" with {current_components['cpu']['socket']} socket"
        print(f"\nSearching ChromaDB for: {mb_query}")
        mb_results = search_components(mb_query, n_results=10)
        mb_components = extract_components_from_results(mb_results, "motherboard", max_components)
        recommendations["motherboards"] = get_db_fallbacks(Motherboard, "motherboard", mb_components, max_components)
        
        # RAM recommendations
        ram_query = f"best RAM for {purpose}"
        print(f"\nSearching ChromaDB for: {ram_query}")
        ram_results = search_components(ram_query, n_results=10)
        ram_components = extract_components_from_results(ram_results, "ram", max_components)
        ram_components = filter_components_for_purpose(ram_components, purpose, "ram", max_components)
        recommendations["ram"] = get_db_fallbacks(RAM, "ram", ram_components, max_components)
        
        # PSU recommendations
        psu_query = f"reliable PSU for {purpose}"
        if 'gpu' in current_components and current_components['gpu'].get('recommended_wattage'):
            psu_query += f" with at least {current_components['gpu']['recommended_wattage']} watts"
        print(f"\nSearching ChromaDB for: {psu_query}")
        psu_results = search_components(psu_query, n_results=10)
        psu_components = extract_components_from_results(psu_results, "psu", max_components)
        recommendations["psus"] = get_db_fallbacks(PSU, "psu", psu_components, max_components)
        
        # Case recommendations
        case_query = f"PC case for {purpose}"
        if 'motherboard' in current_components:
            case_query += f" with {current_components['motherboard']['form_factor']} form factor support"
        print(f"\nSearching ChromaDB for: {case_query}")
        case_results = search_components(case_query, n_results=10)
        case_components = extract_components_from_results(case_results, "case", max_components)
        recommendations["cases"] = get_db_fallbacks(Case, "case", case_components, max_components)
        
        # Storage recommendations
        storage_query = f"storage for {purpose}"
        print(f"\nSearching ChromaDB for: {storage_query}")
        storage_results = search_components(storage_query, n_results=10)
        storage_components = extract_components_from_results(storage_results, "storage", max_components)
        storage_components = filter_components_for_purpose(storage_components, purpose, "storage", max_components)
        recommendations["storage"] = get_db_fallbacks(Storage, "storage", storage_components, max_components)
        
        # Cooler recommendations
        cooler_query = f"CPU cooler for {purpose}"
        print(f"\nSearching ChromaDB for: {cooler_query}")
        cooler_results = search_components(cooler_query, n_results=10)
        cooler_components = extract_components_from_results(cooler_results, "cooler", max_components)
        recommendations["coolers"] = get_db_fallbacks(Cooler, "cooler", cooler_components, max_components)
        
        print(f"\nRecommendations count: CPU={len(recommendations['cpus'])}, GPU={len(recommendations['gpus'])}, MB={len(recommendations['motherboards'])}, RAM={len(recommendations['ram'])}, PSU={len(recommendations['psus'])}, Case={len(recommendations['cases'])}, Storage={len(recommendations['storage'])}, Cooler={len(recommendations['coolers'])}")
        
        # Create simplified component dictionaries
        def simplify_component_data(component_dict):
            """Remove unnecessary fields to reduce token usage"""
            essential_fields = ["id", "name", "price"]  # Always include price
            
            # Add other key fields based on component type
            if "socket" in component_dict:
                essential_fields.append("socket")
            if "cores" in component_dict:
                essential_fields.append("cores")
            if "memory" in component_dict:
                essential_fields.append("memory")
            if "wattage" in component_dict:
                essential_fields.append("wattage")
            if "form_factor" in component_dict:
                essential_fields.append("form_factor")
            if "capacity" in component_dict:
                essential_fields.append("capacity")
            
            return {k: v for k, v in component_dict.items() if k in essential_fields}

        # Then simplify before sending to OpenAI
        simplified_current = {k: simplify_component_data(v) for k, v in current_components.items()}
        simplified_recommendations = {}
        for component_type, components_list in recommendations.items():
            simplified_recommendations[component_type] = [simplify_component_data(c) for c in components_list[:2]]  # Only include top 2

        # Calculate total price before prompt
        current_total = sum(comp.get('price', 0) for comp in simplified_current.values())
        recommended_total = sum(comp.get('price', 0) for comp in simplified_recommendations.values())

        prompt = f"""
        Analyze this PC build for {purpose}:

        Component Priority (1 = highest):
        - 4K Gaming: GPU(1), CPU(2), RAM(3), PSU(4), Storage(5), Case(6), Cooler(7)
        - 1440p Gaming: GPU(1), CPU(2), RAM(3), PSU(4), Storage(5), Case(6), Cooler(7)
        - Workstation: CPU(1), RAM(2), Storage(3), GPU(4), PSU(5), Case(6), Cooler(7)
        - General Use: CPU(1), RAM(2), Storage(3), PSU(4), Case(5), GPU(6), Cooler(7)

        Current build total: {current_total} SEK
        Recommended components total: {recommended_total} SEK

        Current components:
        ```json
        {json.dumps(simplified_current)}
        ```

        Recommended components:
        ```json
        {json.dumps(simplified_recommendations)}
        ```

        Requirements by purpose:
        - 4K Gaming: 
          * GPU: 12GB+ VRAM, RTX 4070 Ti or better
          * CPU: 8+ cores, i7/Ryzen 7 or better
          * RAM: 32GB DDR5, 6000MHz+
          * PSU: 850W+ Gold rated
          * Storage: 1TB+ NVMe SSD
          * Cooling: High-end air or AIO liquid cooler

        - 1440p Gaming:
          * GPU: 8GB+ VRAM, RTX 4060 Ti or better
          * CPU: 6+ cores, i5/Ryzen 5 or better
          * RAM: 16GB DDR4/5, 3600MHz+
          * PSU: 750W+ Bronze rated
          * Storage: 1TB SSD
          * Cooling: Mid-range air cooler

        - Workstation:
          * CPU: 12+ cores, i9/Ryzen 9 or better
          * RAM: 32GB+ DDR5, 4800MHz+
          * GPU: Professional card or high-end gaming GPU
          * PSU: 850W+ Gold rated
          * Storage: 2TB+ NVMe SSD
          * Cooling: High-end air or AIO liquid cooler

        - General Use:
          * CPU: 4+ cores, i3/Ryzen 3 or better
          * RAM: 16GB DDR4, 3200MHz+
          * GPU: Integrated or entry-level discrete
          * PSU: 650W+ Bronze rated
          * Storage: 500GB+ SSD
          * Cooling: Basic air cooler

        Compatibility Rules:
        1. CPU socket must match motherboard socket
        2. Case must support motherboard form factor
        3. PSU wattage must exceed total system requirements by 20%
        4. RAM must be compatible with motherboard (DDR4/DDR5)
        5. Cooler must support CPU socket

        Format:
        {{
          "explanation": "Detailed explanation of needed changes and why",
          "components": {{
            "cpu_id": 1,
            "gpu_id": 2,
            "motherboard_id": 3,
            "ram_id": 4,
            "psu_id": 5,
            "case_id": 6,
            "storage_id": 7,
            "cooler_id": 8
          }}
        }}

        Future-Proofing Guidelines:
        - CPU: Consider socket longevity and upgrade path
        - GPU: Ensure sufficient VRAM for future games
        - RAM: Leave room for expansion
        - Storage: Consider NVMe for future speed requirements
        - PSU: Headroom for future upgrades
        - Case: Support for larger components
        """

        # Before sending to OpenAI
        logger.debug("Sending prompt to OpenAI:\n%s", prompt)

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": """You are a PC building expert specializing in component compatibility and performance optimization. 
                    Your recommendations should:
                    1. Ensure all components are compatible with each other
                    2. Match the user's specific purpose and requirements
                    3. Consider power efficiency and cooling requirements
                    4. Provide detailed explanations for each component choice
                    5. Maintain a reasonable price-to-performance ratio
                    6. Consider future upgrade paths
                    Respond with JSON only."""
                },
                {
                    "role": "user", 
                    "content": prompt + "\n\nRespond with JSON only."
                }
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        print(f"\nOpenAI response: {response.choices[0].message.content}")
        
        # More defensive response handling
        choices = getattr(response, "choices", [])
        if not choices:
            raise ValueError("No choices in OpenAI response")
        
        if not hasattr(choices[0], "message") or not hasattr(choices[0].message, "content"):
            raise ValueError("Invalid response structure from OpenAI")
        
        response_data = choices[0].message.content
        
        # Continue with validation and parsing
        if not response_data.strip().startswith('{'):
            logger.error("Invalid JSON response: %s...", response_data[:100])
            raise ValueError("Invalid JSON response from OpenAI")
        
        result = json.loads(response_data)
        print("DEBUG - OpenAI response parsed successfully")
        
        # Initialize components to preserve current components
        components_dict = {}
        
        # Try to extract components from various possible formats
        if isinstance(result, dict):
            # Format 1: {cpu_id: 123, gpu_id: 456, ...}
            for key in ["cpu_id", "gpu_id", "motherboard_id", "ram_id", "psu_id", "case_id", "storage_id", "cooler_id"]:
                if key in result:
                    components_dict[key] = result[key]
            
            # Format 2: {cpu: {id: 123}, gpu: {id: 456}, ...}
            for key in ["cpu", "gpu", "motherboard", "ram", "psu", "case", "storage", "cooler"]:
                if key in result and isinstance(result[key], dict) and "id" in result[key]:
                    components_dict[f"{key}_id"] = result[key]["id"]
            
            # Format 3: {components: {cpu_id: 123, gpu_id: 456, ...}}
            if "components" in result and isinstance(result["components"], dict):
                for key, value in result["components"].items():
                    if key in ["cpu_id", "gpu_id", "motherboard_id", "ram_id", "psu_id", "case_id", "storage_id", "cooler_id"]:
                        components_dict[key] = value
        
        # Final fallback - use current components if we couldn't extract anything
        result_components = {
            "cpu_id": components_dict.get("cpu_id", request.cpu_id),
            "gpu_id": components_dict.get("gpu_id", request.gpu_id),
            "motherboard_id": components_dict.get("motherboard_id", request.motherboard_id),
            "ram_id": components_dict.get("ram_id", request.ram_id),
            "psu_id": components_dict.get("psu_id", request.psu_id),
            "case_id": components_dict.get("case_id", request.case_id),
            "storage_id": components_dict.get("storage_id", request.storage_id),
            "cooler_id": components_dict.get("cooler_id", request.cooler_id)
        }
        
        # Extract explanation if available
        explanation = result.get("explanation", "No explanation provided")
        
        # Add this function inside the optimize_build function, right before creating the optimized_build object
        def ensure_compatible_cpu_motherboard(components, explanation):
            """Ensure CPU and motherboard are compatible, fixing if needed"""
            if not components.get("cpu_id") or not components.get("motherboard_id"):
                return components, explanation
            
            # Fetch both components
            cpu = db.query(CPU).filter(CPU.id == components["cpu_id"]).first()
            mb = db.query(Motherboard).filter(Motherboard.id == components["motherboard_id"]).first()
            
            if not cpu or not mb or not cpu.socket or not mb.socket:
                return components, explanation
            
            # Normalize sockets for comparison
            cpu_socket = cpu.socket.lower().replace('socket ', '').strip()
            mb_socket = mb.socket.lower().replace('socket ', '').strip()
            
            # Check if compatible
            if cpu_socket == mb_socket or cpu_socket in mb_socket or mb_socket in cpu_socket:
                logger.info(f"CPU {cpu.name} is compatible with motherboard {mb.name}")
                return components, explanation
            
            logger.warning(f"Incompatible components: CPU {cpu.name} ({cpu_socket}) and motherboard {mb.name} ({mb_socket})")
            
            # Try to find a better motherboard for this CPU from our recommendations
            found_compatible_mb = False
            for mb_rec in recommendations.get("motherboards", []):
                rec_mb_socket = mb_rec.get("socket", "").lower().replace('socket ', '').strip()
                if cpu_socket == rec_mb_socket or cpu_socket in rec_mb_socket or rec_mb_socket in cpu_socket:
                    components["motherboard_id"] = mb_rec["id"]
                    logger.info(f"Found compatible motherboard: {mb_rec['name']} for CPU {cpu.name}")
                    explanation += f" NOTE: Updated motherboard to {mb_rec['name']} for compatibility with {cpu.name}."
                    found_compatible_mb = True
                    break
            
            # If no compatible motherboard found, try a compatible CPU instead
            if not found_compatible_mb:
                for cpu_rec in recommendations.get("cpus", []):
                    rec_cpu_socket = cpu_rec.get("socket", "").lower().replace('socket ', '').strip()
                    if rec_cpu_socket == mb_socket or rec_cpu_socket in mb_socket or mb_socket in rec_cpu_socket:
                        components["cpu_id"] = cpu_rec["id"]
                        logger.info(f"Found compatible CPU: {cpu_rec['name']} for motherboard {mb.name}")
                        explanation += f" NOTE: Updated CPU to {cpu_rec['name']} for compatibility with {mb.name}."
                        break
            
            return components, explanation

        # Then before creating the optimized_build, add:
        result_components, explanation = ensure_compatible_cpu_motherboard(result_components, explanation)

        # Fetch components using final IDs
        cpu = get_component_by_id(CPU, result_components["cpu_id"], db)
        if not cpu and result_components["cpu_id"]:
            logger.warning("CPU with ID %s not found in database", result_components["cpu_id"])

        gpu = get_component_by_id(GPU, result_components["gpu_id"], db)
        if not gpu and result_components["gpu_id"]:
            logger.warning("GPU with ID %s not found in database", result_components["gpu_id"])

        motherboard = get_component_by_id(Motherboard, result_components["motherboard_id"], db)
        ram = get_component_by_id(RAM, result_components["ram_id"], db)
        psu = get_component_by_id(PSU, result_components["psu_id"], db)
        case = get_component_by_id(Case, result_components["case_id"], db)
        storage = get_component_by_id(Storage, result_components["storage_id"], db)
        cooler = get_component_by_id(Cooler, result_components["cooler_id"], db)

        # Create the optimized build 
        optimized_build = OptimizedBuildOut(
            id=1,
            name="Optimized Build",
            purpose=purpose,
            user_id=current_user.id,
            cpu_id=result_components["cpu_id"],
            gpu_id=result_components["gpu_id"],
            motherboard_id=result_components["motherboard_id"],
            ram_id=result_components["ram_id"],
            psu_id=result_components["psu_id"],
            case_id=result_components["case_id"],
            storage_id=result_components["storage_id"],
            cooler_id=result_components["cooler_id"],
            cpu=cpu,
            gpu=gpu,
            motherboard=motherboard,
            ram=ram,
            psu=psu,
            case=case,
            storage=storage,
            cooler=cooler,
            explanation=explanation,
            similarity_score=0.95,
            created_at=current_time,
            updated_at=current_time
        )

        print("\n==== OPTIMIZE BUILD COMPLETE ====\n")
        return optimized_build
        
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"ERROR parsing OpenAI response: {str(e)}")
        # Return a basic response with original components to avoid breaking the UI
        raise HTTPException(
            status_code=400, 
            detail=f"Error processing optimization response: {str(e)}"
        )

def extract_component_id(result, component_key):
    """Extract component ID from various response formats"""
    # Format 1: {cpu_id: 123, ...}
    component_id_key = f"{component_key}_id"
    if component_id_key in result:
        return result[component_id_key]
    
    # Format 2: {cpu: {id: 123}, ...}
    if component_key in result and isinstance(result[component_key], dict) and "id" in result[component_key]:
        return result[component_key]["id"]
    
    # Format 3: {components: {cpu_id: 123, ...}}
    if "components" in result and isinstance(result["components"], dict):
        if component_id_key in result["components"]:
            return result["components"][component_id_key]
    
    return None

def get_component_by_id(model, component_id, db, cache=None):
    """Fetch component by ID with caching"""
    if cache is None:
        cache = {}
        
    cache_key = f"{model.__name__}_{component_id}"
    if cache_key not in cache and component_id:
        cache[cache_key] = db.query(model).filter(model.id == component_id).first()
    return cache.get(cache_key)
