from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from core.deps import get_current_user
from schemas import OptimizationRequest, OptimizedBuildOut, ComponentAnalysis
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
from sqlalchemy import or_

router = APIRouter()
logger = logging.getLogger(__name__)

# Helper function to extract gigabyte values
def extract_gb(memory_str):
    """Extract gigabyte value from memory strings like '12GB', '8 GB', etc."""
    if not memory_str or not isinstance(memory_str, str):
        return None
    
    match = re.search(r"(\d+(?:\.\d+)?)\s*gb", memory_str.lower())
    if match:
        return float(match.group(1))
    return None

# Helper function to normalize socket names
def normalize_socket(socket_str):
    """Normalize socket strings for consistent comparison"""
    if not socket_str:
        return ""
        
    # Convert to string and lowercase
    socket = str(socket_str).lower().strip()
    
    # Remove "socket" prefix if present
    if socket.startswith("socket "):
        socket = socket[7:].strip()
    
    # Handle common variations
    return socket

# Helper function to normalize form factors consistently with frontend
def normalize_form_factor(form_factor):
    """Normalize form factor strings for consistent handling"""
    if not form_factor:
        return ''
    
    # Convert to string in case it's not
    ff = str(form_factor).lower().strip()
    
    # Handle common variations and Swedish translations
    if 'utökad' in ff or 'extended' in ff or 'e-atx' in ff:
        return 'e-atx'
    if 'ssi eeb' in ff or 'eeb' in ff:
        return 'ssi-eeb'
    if 'micro' in ff:
        return 'micro-atx'
    if 'mini-mini' in ff:
        return 'mini-itx'
    if 'mini' in ff:
        return 'mini-itx'
    if ff == 'itx':
        return 'mini-itx'  # Explicitly handle ITX as mini-itx
    if 'itx' in ff:
        return 'mini-itx'  # Handle any variant containing ITX
    if ff == 'atx' or ('atx' in ff and 'micro' not in ff and 'mini' not in ff):
        return 'atx'
    
    # Log unexpected form factors
    logger.warning(f"Unexpected form factor: {form_factor}")
    return ff  # Return lowercase trimmed version

# Process form factors that might contain multiple values
def handle_multiple_form_factors(form_factor_string):
    """Handle form factor strings that might contain multiple values separated by commas"""
    if not form_factor_string or not isinstance(form_factor_string, str):
        return []
        
    # Split by commas or similar separators
    form_factors = re.split(r'[,;/]', form_factor_string)
    # Normalize each form factor
    normalized = [normalize_form_factor(ff.strip()) for ff in form_factors if ff.strip()]
    # Return unique form factors
    return list(set(normalized))

# Helper function to simplify component data for token reduction
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
        # Normalize form factor if it exists
        if component_dict.get("form_factor"):
            try:
                component_dict["normalized_form_factor"] = normalize_form_factor(component_dict["form_factor"])
                essential_fields.append("normalized_form_factor")
            except Exception as e:
                logger.warning(f"Error normalizing form factor '{component_dict.get('form_factor')}': {e}")
    if "capacity" in component_dict:
        essential_fields.append("capacity")
    
    return {k: v for k, v in component_dict.items() if k in essential_fields}

# Form factor compatibility mapping
form_factor_compatibility = {
    "ssi-eeb": ["ssi-eeb", "e-atx", "atx", "micro-atx", "mini-itx"],
    "e-atx": ["e-atx", "atx", "micro-atx", "mini-itx"],
    "atx": ["atx", "micro-atx", "mini-itx"],
    "micro-atx": ["micro-atx", "mini-itx"],
    "mini-itx": ["mini-itx"]
}

# Helper function to check case and motherboard form factor compatibility
def is_case_compatible_with_motherboard(case_form_factor, motherboard_form_factor):
    """
    Check if a case can fit a motherboard based on their form factors
    
    Args:
        case_form_factor: Normalized form factor of the case
        motherboard_form_factor: Normalized form factor of the motherboard
        
    Returns:
        Boolean indicating whether the case can fit the motherboard
    """
    # Handle empty values
    if not case_form_factor or not motherboard_form_factor:
        return False
        
    # Check if case form factor is in our compatibility mapping
    if case_form_factor in form_factor_compatibility:
        compatible_form_factors = form_factor_compatibility[case_form_factor]
        return motherboard_form_factor in compatible_form_factors
        
    # If we don't have the case form factor in our mapping, check for substring match
    return motherboard_form_factor in case_form_factor

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
        
        # Current logic processes a request to optimize a PC build
        # Let's analyze the current components first before making recommendations
        
        # Initialize analytics for current components
        component_analysis = {
            "analysis": [],
            "missing_components": [],
            "compatibility_issues": [],
            "suggested_upgrades": []
        }
        
        # Check if required components are missing
        essential_components = ["cpu", "motherboard", "ram", "psu", "storage"]
        for comp in essential_components:
            if comp not in current_components:
                message = f"Din dator saknar {comp} (translated component name)."
                component_analysis["missing_components"].append({
                    "component_type": comp,
                    "message": message
                })
        
        # Analyze compatibility of existing components
        if "cpu" in current_components and "motherboard" in current_components:
            cpu_socket = normalize_socket(current_components["cpu"]["socket"]) if current_components["cpu"].get("socket") else ""
            mb_socket = normalize_socket(current_components["motherboard"]["socket"]) if current_components["motherboard"].get("socket") else ""
            
            if cpu_socket and mb_socket:
                # Normalize socket names for comparison
                cpu_socket = cpu_socket.replace('socket ', '').strip()
                mb_socket = mb_socket.replace('socket ', '').strip()
                
                # Special case for Socket 1851
                if "1851" in cpu_socket or "1851" in mb_socket:
                    if "1851" not in cpu_socket or "1851" not in mb_socket:
                        component_analysis["compatibility_issues"].append({
                            "component_types": ["cpu", "motherboard"],
                            "message": "CPU och moderkort är inte kompatibla. Socket 1851 (Intel Ultra) kräver särskilt moderkort."
                        })
                # Special case for AM4/AM5
                elif (cpu_socket == "am4" and mb_socket != "am4") or (cpu_socket == "am5" and mb_socket != "am5"):
                    component_analysis["compatibility_issues"].append({
                        "component_types": ["cpu", "motherboard"],
                        "message": f"CPU Socket {cpu_socket.upper()} är inte kompatibel med moderkort socket {mb_socket.upper()}."
                    })
                # General compatibility check
                elif not (cpu_socket in mb_socket or mb_socket in cpu_socket):
                    component_analysis["compatibility_issues"].append({
                        "component_types": ["cpu", "motherboard"],
                        "message": f"CPU Socket {cpu_socket.upper()} och moderkort socket {mb_socket.upper()} är inte kompatibla."
                    })
        
        # Analyze motherboard and case compatibility
        if "motherboard" in current_components and "case" in current_components:
            mobo_ff = normalize_form_factor(current_components["motherboard"].get("form_factor", ""))
            case_ff = normalize_form_factor(current_components["case"].get("form_factor", ""))
            
            if mobo_ff and case_ff:
                if case_ff in form_factor_compatibility:
                    compatible_ffs = form_factor_compatibility[case_ff]
                    if mobo_ff not in compatible_ffs:
                        component_analysis["compatibility_issues"].append({
                            "component_types": ["motherboard", "case"],
                            "message": f"Moderkortets formfaktor ({mobo_ff}) passar inte i chassit ({case_ff})."
                        })
                else:
                    logger.warning(f"Unknown case form factor for compatibility check: {case_ff}")
        
        # Check if PSU has enough wattage for GPU
        if "gpu" in current_components and "psu" in current_components:
            gpu_wattage = 0
            if current_components["gpu"].get("recommended_wattage"):
                try:
                    gpu_wattage = int(current_components["gpu"]["recommended_wattage"])
                except (ValueError, TypeError):
                    gpu_wattage = 0
            else:
                # Estimate based on GPU memory if available
                if current_components["gpu"].get("memory"):
                    try:
                        memory_gb = extract_gb(current_components["gpu"]["memory"])
                        if memory_gb:
                            # Rough estimation based on VRAM
                            gpu_wattage = 75 + (memory_gb * 20)
                    except Exception as e:
                        logger.error(f"Error estimating GPU wattage: {str(e)}")
            
            # Minimum system wattage = GPU + base components (CPU, motherboard, etc.)
            min_system_wattage = gpu_wattage + 150  # Base system wattage
            if "cpu" in current_components:
                min_system_wattage += 100  # Typical CPU wattage
            
            recommended_wattage = int(min_system_wattage * 1.2)  # Add 20% headroom
            
            psu_wattage = 0
            try:
                psu_wattage = int(current_components["psu"].get("wattage", 0))
            except (ValueError, TypeError):
                psu_wattage = 0
            
            if psu_wattage < recommended_wattage:
                component_analysis["compatibility_issues"].append({
                    "component_types": ["gpu", "psu"],
                    "message": f"Nätaggregatet ({psu_wattage}W) kan vara för svagt för ditt grafikkort. Vi rekommenderar minst {recommended_wattage}W."
                })
        
        # Analyze components for purpose-specific suitability
        purpose_lower = purpose.lower()
        
        # Check if RAM is sufficient for the purpose
        if "ram" in current_components:
            ram_capacity = 0
            if current_components["ram"].get("capacity"):
                try:
                    ram_capacity = float(current_components["ram"]["capacity"])
                except (ValueError, TypeError):
                    ram_str = str(current_components["ram"]["capacity"])
                    ram_match = re.search(r"(\d+(?:\.\d+)?)", ram_str)
                    if ram_match:
                        ram_capacity = float(ram_match.group(1))
            
            needed_ram = 8  # Default minimal RAM
            if "gaming" in purpose_lower:
                if "4k" in purpose_lower:
                    needed_ram = 32
                else:
                    needed_ram = 16
            elif any(p in purpose_lower for p in ["utveckling", "development", "programmering", "coding"]):
                needed_ram = 16
            elif any(p in purpose_lower for p in ["video", "editing", "redigering", "rendering"]):
                needed_ram = 32
            elif any(p in purpose_lower for p in ["ai", "machine learning", "deep learning"]):
                needed_ram = 32
            
            if ram_capacity < needed_ram:
                component_analysis["suggested_upgrades"].append({
                    "component_type": "ram",
                    "message": f"För '{purpose}' rekommenderas minst {int(needed_ram)}GB RAM. Du har {int(ram_capacity)}GB."
                })
        
        # Check if GPU is suitable for 4K gaming
        if "gaming" in purpose_lower and "4k" in purpose_lower and "gpu" in current_components:
            gpu_vram = extract_gb(current_components["gpu"].get("memory", ""))
            
            if gpu_vram is not None and gpu_vram < 8:
                component_analysis["suggested_upgrades"].append({
                    "component_type": "gpu",
                    "message": f"För 4K-gaming rekommenderas ett grafikkort med minst 8GB VRAM. Ditt kort har endast {int(gpu_vram)}GB."
                })
        
        # Add the component analysis to the API response
        processed_components = {}
        for comp_type, comp in current_components.items():
            processed_components[comp_type] = simplify_component_data(comp)
        
        # Check if we are starting with no components - if so, populate suggestions
        if not current_components:
            component_analysis["analysis"].append({
                "message": "Du har inte valt några komponenter än. Här är förslag på komponenter baserat på ditt användningsområde."
            })

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
        
        # Then simplify before sending to OpenAI
        try:
            simplified_current = {k: simplify_component_data(v) for k, v in current_components.items()}
            simplified_recommendations = {}
            for component_type, components_list in recommendations.items():
                if not components_list:
                    logger.warning(f"Empty component list for {component_type}")
                    simplified_recommendations[component_type] = []
                    continue
                
                try:
                    simplified_recommendations[component_type] = [simplify_component_data(c) for c in components_list[:2] if c]  # Only include top 2
                except Exception as e:
                    logger.error(f"Error simplifying {component_type}: {str(e)}")
                    simplified_recommendations[component_type] = []
                
            # Calculate total price before prompt
            current_total = sum(comp.get('price', 0) or 0 for comp in simplified_current.values())
            
            # Fix: Handle the case where simplified_recommendations.values() contains lists
            recommended_total = 0
            for component_list in simplified_recommendations.values():
                if component_list and isinstance(component_list, list):
                    for comp in component_list:
                        recommended_total += comp.get('price', 0) or 0
            
            logger.info(f"Current total: {current_total}, Recommended total: {recommended_total}")
            
        except Exception as e:
            logger.error(f"Error preparing recommendation data: {e}")
            logger.error(traceback.format_exc())
            # Continue with empty recommendations if there's an error
            simplified_current = {}
            simplified_recommendations = {}
            current_total = 0
            recommended_total = 0

        # Fix the f-string format by using proper escaping for nested curly braces
        try:
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
            
            logger.info("Generated prompt successfully")
            
            # Extract individual components for the response
            # Get the first recommended component of each type, or None if not available
            selected_cpu = simplified_recommendations.get("cpus", [None])[0] if simplified_recommendations.get("cpus") else None
            selected_gpu = simplified_recommendations.get("gpus", [None])[0] if simplified_recommendations.get("gpus") else None
            selected_motherboard = simplified_recommendations.get("motherboards", [None])[0] if simplified_recommendations.get("motherboards") else None
            selected_ram = simplified_recommendations.get("ram", [None])[0] if simplified_recommendations.get("ram") else None
            selected_psu = simplified_recommendations.get("psus", [None])[0] if simplified_recommendations.get("psus") else None
            selected_case = simplified_recommendations.get("cases", [None])[0] if simplified_recommendations.get("cases") else None
            selected_storage = simplified_recommendations.get("storage", [None])[0] if simplified_recommendations.get("storage") else None
            selected_cooler = simplified_recommendations.get("coolers", [None])[0] if simplified_recommendations.get("coolers") else None
            
            # Fix: Don't nest the required fields inside 'data'
            return {
                "id": 1,  # Adding required fields for OptimizedBuildOut model
                "name": "Optimized Build",
                "user_id": current_user.id if current_user else 1,
                "created_at": current_time,
                "updated_at": current_time,
                "explanation": "PC build optimization",
                "similarity_score": 0.85,
                "prompt": prompt,
                "current_components": simplified_current,
                "recommended_components": simplified_recommendations,
                "current_total": current_total,
                "recommended_total": recommended_total,
                "purpose": request.purpose,
                # Add individual components to the response
                "cpu": selected_cpu,
                "gpu": selected_gpu,
                "motherboard": selected_motherboard,
                "ram": selected_ram,
                "psu": selected_psu,
                "case": selected_case,
                "storage": selected_storage,
                "cooler": selected_cooler,
                # Add component analysis for better debugging
                "component_analysis": component_analysis
            }
        except Exception as e:
            logger.error(f"Error generating prompt: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "message": "An error occurred while generating the optimization prompt."
            }
    except Exception as e:
        logger.error(f"Error in optimize_build: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "message": "An error occurred while optimizing the build."
        }