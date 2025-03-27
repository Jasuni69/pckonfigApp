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

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/build", response_model=OptimizedBuildOut)
async def optimize_build(
    request: OptimizationRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Received optimization request: {request}")
        
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

        # Define the purpose for component search
        purpose = request.purpose or "general use"
        
        # Function to extract and format component data from ChromaDB results
        def extract_components_from_results(results, component_type, limit=3):
            components = []
            if not results or "metadatas" not in results or not results["metadatas"][0]:
                return components
                
            for i, metadata in enumerate(results["metadatas"][0]):
                if metadata.get("type", "").lower() == component_type.lower():
                    try:
                        # Extract the ID from the component ID string (e.g., "cpu_1" -> 1)
                        component_id = metadata.get("id")
                        if not component_id and "id" in results["ids"][0][i]:
                            # Try to extract from the ID if it's something like "cpu_1"
                            id_parts = results["ids"][0][i].split("_")
                            if len(id_parts) > 1 and id_parts[1].isdigit():
                                component_id = int(id_parts[1])
                        
                        # Only add components with valid IDs
                        if component_id:
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
                                    "recommended_wattage": metadata.get("recommended_wattage", 0),
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
                            if len(components) >= limit:
                                break
                    except Exception as e:
                        logger.error(f"Error extracting {component_type} data: {str(e)}")
            
            return components
        
        # Function to get database fallbacks if ChromaDB doesn't return enough results
        def get_db_fallbacks(model, component_type, existing_components, limit=3):
            needed = limit - len(existing_components)
            if needed <= 0:
                return existing_components
                
            # Get IDs of existing components to avoid duplicates
            existing_ids = [c["id"] for c in existing_components]
            
            # Query for additional components, excluding existing ones
            additional_components = []
            db_components = db.query(model).filter(model.id.not_in(existing_ids)).order_by(model.price.desc()).limit(needed).all()
            
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
                        "memory": getattr(comp, 'memory', None),
                        "recommended_wattage": getattr(comp, 'recommended_wattage', None)
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
            
            return existing_components + additional_components
        
        # Prepare component recommendations using ChromaDB
        recommendations = {}
        max_components = 3  # Maximum number of components per type to include
        
        # CPU recommendations
        cpu_query = f"best CPU for {purpose}"
        cpu_results = search_components(cpu_query, n_results=max_components)
        cpu_components = extract_components_from_results(cpu_results, "CPU", max_components)
        recommendations["cpus"] = get_db_fallbacks(CPU, "cpu", cpu_components, max_components)
        
        # GPU recommendations
        gpu_query = f"best GPU for {purpose}"
        gpu_results = search_components(gpu_query, n_results=max_components)
        gpu_components = extract_components_from_results(gpu_results, "GPU", max_components)
        recommendations["gpus"] = get_db_fallbacks(GPU, "gpu", gpu_components, max_components)
        
        # Motherboard recommendations
        mb_query = f"compatible motherboard for {purpose}"
        if 'cpu' in current_components:
            mb_query += f" with {current_components['cpu']['socket']} socket"
        mb_results = search_components(mb_query, n_results=max_components)
        mb_components = extract_components_from_results(mb_results, "Motherboard", max_components)
        recommendations["motherboards"] = get_db_fallbacks(Motherboard, "motherboard", mb_components, max_components)
        
        # RAM recommendations
        ram_query = f"best RAM for {purpose}"
        ram_results = search_components(ram_query, n_results=max_components)
        ram_components = extract_components_from_results(ram_results, "RAM", max_components)
        recommendations["ram"] = get_db_fallbacks(RAM, "ram", ram_components, max_components)
        
        # PSU recommendations
        psu_query = f"reliable PSU for {purpose}"
        if 'gpu' in current_components and current_components['gpu'].get('recommended_wattage'):
            psu_query += f" with at least {current_components['gpu']['recommended_wattage']} watts"
        psu_results = search_components(psu_query, n_results=max_components)
        psu_components = extract_components_from_results(psu_results, "PSU", max_components)
        recommendations["psus"] = get_db_fallbacks(PSU, "psu", psu_components, max_components)
        
        # Case recommendations
        case_query = f"PC case for {purpose}"
        if 'motherboard' in current_components:
            case_query += f" with {current_components['motherboard']['form_factor']} form factor support"
        case_results = search_components(case_query, n_results=max_components)
        case_components = extract_components_from_results(case_results, "Case", max_components)
        recommendations["cases"] = get_db_fallbacks(Case, "case", case_components, max_components)
        
        # Storage recommendations
        storage_query = f"storage for {purpose}"
        storage_results = search_components(storage_query, n_results=max_components)
        storage_components = extract_components_from_results(storage_results, "Storage", max_components)
        recommendations["storage"] = get_db_fallbacks(Storage, "storage", storage_components, max_components)
        
        # Cooler recommendations
        cooler_query = f"CPU cooler for {purpose}"
        cooler_results = search_components(cooler_query, n_results=max_components)
        cooler_components = extract_components_from_results(cooler_results, "Cooler", max_components)
        recommendations["coolers"] = get_db_fallbacks(Cooler, "cooler", cooler_components, max_components)
        
        # Create a concise prompt for OpenAI
        prompt = f"""
        Analyze this PC build for {purpose}:

        Current components:
        {json.dumps(current_components, indent=2)}

        Recommended components (filtered for {purpose}):
        {json.dumps(recommendations, indent=2)}

        Based on the purpose "{purpose}", evaluate if any components need upgrading.
        If upgrades are needed, recommend specific components by ID from the recommendations.
        If the current build is already well-suited for the purpose, indicate that no changes are needed.

        Return a JSON with:
        1. A brief explanation
        2. Component IDs to use (keep current IDs if no change needed)

        Format as:
        {{
          "explanation": "Explanation text",
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
        """
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a PC building expert. Evaluate if the current build is suitable for the user's purpose. If upgrades are needed, recommend specific component upgrades from the provided options."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        try:
            result = json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            logger.error("Failed to parse response as JSON")
            explanation_text = response.choices[0].message.content
            result = {
                "explanation": explanation_text,
                "components": {}
            }
        
        # Create the optimized build
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
            explanation=result["explanation"],
            similarity_score=0.95,
            created_at=current_time,
            updated_at=current_time
        )
        
        return optimized_build
        
    except Exception as e:
        error_msg = f"Error in optimize_build: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=error_msg
        )
