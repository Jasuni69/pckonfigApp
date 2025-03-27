from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from core.deps import get_current_user
from schemas import OptimizationRequest, OptimizedBuildOut
from models import CPU, GPU, RAM, PSU, Case, Storage, Cooler, Motherboard
from ChromaDB.manager import search_components
from typing import List, Dict, Any
import logging
import json
import openai
from datetime import datetime
import traceback
import sys

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/build", response_model=OptimizedBuildOut)
async def optimize_build(
    request: OptimizationRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        print("\n==== OPTIMIZE BUILD START ====\n")
        print(f"Received optimization request for purpose: {request.purpose}")
        
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

        print(f"Current components: {json.dumps(current_components, indent=2)}")
        
        # Define the purpose for component search
        purpose = request.purpose or "general use"
        
        # Function to extract and format component data from ChromaDB results
        def extract_components_from_results(results, component_type, limit=3):
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
                    query = query.filter(model.id.not_in(existing_ids))
                
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
        def validate_gpu_for_4k(gpu):
            if not gpu:
                return False
            
            # Handle both dictionary and Pydantic model
            if hasattr(gpu, 'model_dump'):  # Pydantic v2
                gpu_data = gpu.model_dump()
            elif hasattr(gpu, 'dict'):  # Pydantic v1
                gpu_data = gpu.dict()
            else:  # Plain dictionary
                gpu_data = gpu
            
            memory = gpu_data.get('memory', '')
            if not memory:
                return False
            
            try:
                memory_value = float(memory.split()[0])  # Extract number from "16 GB"
                return memory_value >= 12
            except (ValueError, AttributeError):
                return False
        
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

        gpu_components = filter_components_for_purpose(gpu_components, purpose, "gpu", max_components)
        print(f"Filtered GPU components:")
        print(json.dumps(gpu_components, indent=2))

        recommendations["gpus"] = get_db_fallbacks(GPU, "gpu", gpu_components, max_components)
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
        
        # Then update the prompt and API call
        messages = [
            {"role": "system", "content": """You are a PC building expert. 
            When optimizing builds, follow these guidelines:
            1. For 4K gaming, the GPU MUST have at least 12GB VRAM
            2. Evaluate each current component - only suggest upgrades if they provide meaningful improvement
            3. Consider the overall system balance and compatibility
            4. If the current component is already suitable, keep it
            
            Respond ONLY with a JSON object containing:
            1. explanation: string explaining your recommendations and why specific upgrades are needed
            2. components: object with component IDs (cpu_id, gpu_id, etc.) - use null to keep current component
            """},
            
            {"role": "user", "content": f"""
            Current build purpose: {purpose}
            Current components: {json.dumps(current_components, indent=2)}
            
            Available upgrade options:
            CPUs: {json.dumps(cpu_components, indent=2)}
            GPUs: {json.dumps(gpu_components, indent=2)}
            Motherboards: {json.dumps(mb_components, indent=2)}
            RAM: {json.dumps(ram_components, indent=2)}
            PSUs: {json.dumps(psu_components, indent=2)}
            Cases: {json.dumps(case_components, indent=2)}
            Storage: {json.dumps(storage_components, indent=2)}
            Coolers: {json.dumps(cooler_components, indent=2)}
            
            Guidelines for {purpose}:
            1. For 4K gaming, ensure the GPU has at least 12GB VRAM
            2. Evaluate if current components meet the performance requirements
            3. Only suggest upgrades that provide meaningful improvement
            4. Consider value for money in recommendations
            
            Respond with a JSON object containing your recommendations and explanation.
            """}
        ]
        
        print(f"\nSending prompt to OpenAI")
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        print(f"\nOpenAI response: {response.choices[0].message.content}")
        
        # Parse the response
        try:
            result = json.loads(response.choices[0].message.content)
            print(f"\nParsed result: {json.dumps(result, indent=2)}")
        except json.JSONDecodeError:
            print("Failed to parse response as JSON")
            explanation_text = response.choices[0].message.content
            result = {
                "explanation": explanation_text,
                "components": {}
            }
        
        # Ensure the components object exists
        if "components" not in result:
            result["components"] = {}
        
        # Fetch the full component objects from the database
        cpu = db.query(CPU).filter(CPU.id == result["components"].get("cpu_id", request.cpu_id)).first() if result["components"].get("cpu_id", request.cpu_id) else None
        gpu = db.query(GPU).filter(GPU.id == result["components"].get("gpu_id", request.gpu_id)).first() if result["components"].get("gpu_id", request.gpu_id) else None
        motherboard = db.query(Motherboard).filter(Motherboard.id == result["components"].get("motherboard_id", request.motherboard_id)).first() if result["components"].get("motherboard_id", request.motherboard_id) else None
        ram = db.query(RAM).filter(RAM.id == result["components"].get("ram_id", request.ram_id)).first() if result["components"].get("ram_id", request.ram_id) else None
        psu = db.query(PSU).filter(PSU.id == result["components"].get("psu_id", request.psu_id)).first() if result["components"].get("psu_id", request.psu_id) else None
        case = db.query(Case).filter(Case.id == result["components"].get("case_id", request.case_id)).first() if result["components"].get("case_id", request.case_id) else None
        storage = db.query(Storage).filter(Storage.id == result["components"].get("storage_id", request.storage_id)).first() if result["components"].get("storage_id", request.storage_id) else None
        cooler = db.query(Cooler).filter(Cooler.id == result["components"].get("cooler_id", request.cooler_id)).first() if result["components"].get("cooler_id", request.cooler_id) else None

        print(f"\nFetched component objects:")
        print(f"CPU: {cpu}")
        print(f"GPU: {gpu}")
        print(f"Motherboard: {motherboard}")
        print(f"RAM: {ram}")
        print(f"PSU: {psu}")
        print(f"Case: {case}")
        print(f"Storage: {storage}")
        print(f"Cooler: {cooler}")

        # Add this just after fetching component objects
        print(f"\nComponent IDs:")
        print(f"CPU ID: {result['components'].get('cpu_id', request.cpu_id)}")
        print(f"GPU ID: {result['components'].get('gpu_id', request.gpu_id)}")
        print(f"Motherboard ID: {result['components'].get('motherboard_id', request.motherboard_id)}")
        print(f"RAM ID: {result['components'].get('ram_id', request.ram_id)}")
        print(f"PSU ID: {result['components'].get('psu_id', request.psu_id)}")
        print(f"Case ID: {result['components'].get('case_id', request.case_id)}")
        print(f"Storage ID: {result['components'].get('storage_id', request.storage_id)}")
        print(f"Cooler ID: {result['components'].get('cooler_id', request.cooler_id)}")

        # After getting the OpenAI response, validate requirements
        try:
            response_data = response.choices[0].message.content
            result = json.loads(response_data)
            
            # For 4K gaming, ensure GPU meets requirements
            if purpose.lower() == "4k gaming":
                # Check if explanation and actual selection match
                gpu_id = result["components"].get("gpu_id")
                
                # If keeping current GPU, check if it meets requirements
                if gpu_id is None:
                    current_gpu = current_components.get("gpu", {})
                    if not validate_gpu_for_4k(current_gpu):
                        # Force selection of a new GPU
                        suitable_gpus = [g for g in gpu_components if validate_gpu_for_4k(g)]
                        if suitable_gpus:
                            result["components"]["gpu_id"] = suitable_gpus[0]["id"]
                            result["explanation"] = "Upgraded GPU to meet 4K gaming requirements. " + result["explanation"]
                        else:
                            raise ValueError("No suitable GPU found for 4K gaming")
                else:
                    # If selecting new GPU, validate it
                    selected_gpu = next((g for g in gpu_components if g["id"] == gpu_id), None)
                    if not selected_gpu or not validate_gpu_for_4k(selected_gpu):
                        suitable_gpus = [g for g in gpu_components if validate_gpu_for_4k(g)]
                        if suitable_gpus:
                            result["components"]["gpu_id"] = suitable_gpus[0]["id"]
                            result["explanation"] = "Selected a more suitable GPU for 4K gaming. " + result["explanation"]
                        else:
                            raise ValueError("Selected GPU does not meet 4K gaming requirements")

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error validating OpenAI response: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error in optimize_build: {str(e)}")

        # Create the optimized build with both IDs and full component objects
        optimized_build = OptimizedBuildOut(
            id=1,
            name="Optimized Build",
            purpose=purpose,
            user_id=current_user.id,
            cpu_id=result["components"].get("cpu_id", request.cpu_id),
            gpu_id=result["components"].get("gpu_id", request.gpu_id),
            motherboard_id=result["components"].get("motherboard_id", request.motherboard_id),
            ram_id=result["components"].get("ram_id", request.ram_id),
            psu_id=result["components"].get("psu_id", request.psu_id),
            case_id=result["components"].get("case_id", request.case_id),
            storage_id=result["components"].get("storage_id", request.storage_id),
            cooler_id=result["components"].get("cooler_id", request.cooler_id),
            cpu=cpu,
            gpu=gpu,
            motherboard=motherboard,
            ram=ram,
            psu=psu,
            case=case,
            storage=storage,
            cooler=cooler,
            explanation=result.get("explanation", "No explanation provided"),
            similarity_score=0.95,
            created_at=current_time,
            updated_at=current_time
        )
        
        try:
            # For Pydantic v2
            if hasattr(optimized_build, "model_dump"):
                result_dict = optimized_build.model_dump()
                print(f"Serialized result (model_dump): {json.dumps(result_dict, default=str)}")
            # For Pydantic v1
            elif hasattr(optimized_build, "dict"):
                result_dict = optimized_build.dict()
                print(f"Serialized result (dict): {json.dumps(result_dict, default=str)}")
            else:
                print("Unable to serialize optimized_build - no model_dump or dict method found")
        except Exception as e:
            print(f"Error serializing optimized_build: {str(e)}")
            print(traceback.format_exc())

        print("\n==== OPTIMIZE BUILD COMPLETE ====\n")
        return optimized_build
        
    except Exception as e:
        error_msg = f"Error in optimize_build: {str(e)}"
        print(f"\n==== ERROR IN OPTIMIZE BUILD ====\n")
        print(error_msg)
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500, 
            detail=error_msg
        )
