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
        
        if request.gpu_id:
            gpu = db.query(GPU).filter(GPU.id == request.gpu_id).first()
            if gpu:
                current_components["gpu"] = {
                    "id": gpu.id,
                    "name": gpu.name,
                    "price": gpu.price,
                    # Add other relevant GPU fields
                }
        
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
        
        if request.ram_id:
            ram = db.query(RAM).filter(RAM.id == request.ram_id).first()
            if ram:
                current_components["ram"] = {
                    "id": ram.id,
                    "name": ram.name,
                    "capacity": ram.capacity,
                    "price": ram.price
                }
        
        if request.psu_id:
            psu = db.query(PSU).filter(PSU.id == request.psu_id).first()
            if psu:
                current_components["psu"] = {
                    "id": psu.id,
                    "name": psu.name,
                    "wattage": psu.wattage,
                    "price": psu.price
                }
        
        if request.case_id:
            case = db.query(Case).filter(Case.id == request.case_id).first()
            if case:
                current_components["case"] = {
                    "id": case.id,
                    "name": case.name,
                    "form_factor": case.form_factor,
                    "price": case.price
                }
        
        if request.storage_id:
            storage = db.query(Storage).filter(Storage.id == request.storage_id).first()
            if storage:
                current_components["storage"] = {
                    "id": storage.id,
                    "name": storage.name,
                    "capacity": storage.capacity,
                    "price": storage.price
                }
        
        if request.cooler_id:
            cooler = db.query(Cooler).filter(Cooler.id == request.cooler_id).first()
            if cooler:
                current_components["cooler"] = {
                    "id": cooler.id,
                    "name": cooler.name,
                    "price": cooler.price
                }

        # Get all available components
        all_cpus = [{"id": c.id, "name": c.name, "socket": c.socket, "cores": c.cores, "price": c.price} 
                   for c in db.query(CPU).all()]
        all_gpus = [{"id": c.id, "name": c.name, "price": c.price} 
                   for c in db.query(GPU).all()]
        all_motherboards = [{"id": c.id, "name": c.name, "socket": c.socket, "form_factor": c.form_factor, "price": c.price} 
                           for c in db.query(Motherboard).all()]
        all_ram = [{"id": c.id, "name": c.name, "capacity": c.capacity, "price": c.price} 
                   for c in db.query(RAM).all()]
        all_psus = [{"id": c.id, "name": c.name, "wattage": c.wattage, "price": c.price} 
                   for c in db.query(PSU).all()]
        all_cases = [{"id": c.id, "name": c.name, "form_factor": c.form_factor, "price": c.price} 
                   for c in db.query(Case).all()]
        all_storage = [{"id": c.id, "name": c.name, "capacity": c.capacity, "price": c.price} 
                   for c in db.query(Storage).all()]
        all_coolers = [{"id": c.id, "name": c.name, "price": c.price} 
                   for c in db.query(Cooler).all()]
        
        # Ask AI to optimize the build
        prompt = f"""
        Analyze this PC build for {request.purpose}:
        
        Current components:
        {json.dumps(current_components, indent=2)}
        
        Available CPUs:
        {json.dumps(all_cpus, indent=2)}
        
        Available GPUs:
        {json.dumps(all_gpus, indent=2)}
        
        Available Motherboards:
        {json.dumps(all_motherboards, indent=2)}
        
        Available RAM:
        {json.dumps(all_ram, indent=2)}
        
        Available PSUs:
        {json.dumps(all_psus, indent=2)}
        
        Available Cases:
        {json.dumps(all_cases, indent=2)}
        
        Available Storage:
        {json.dumps(all_storage, indent=2)}
        
        Available Coolers:
        {json.dumps(all_coolers, indent=2)}
        
        Based on the purpose "{request.purpose}", evaluate if any components need upgrading.
        If upgrades are needed, recommend specific components by ID that would be better suited.
        If the current build is missing any components, recommend specific ones to add.
        If the current build is already well-suited for the purpose, you can indicate that no changes are needed.
        
        Return a single optimized build with:
        1. Which components to keep
        2. Which components to replace (if any) with specific IDs and why
        3. A brief explanation of the changes or why no changes are needed
        
        Format as JSON:
        {{
          "explanation": "Overall explanation of changes or why the build is already suitable",
          "changes": [
            {{ "component": "gpu", "from_id": 123, "to_id": 456, "reason": "The 4060 is not powerful enough for 4K gaming" }}
          ],
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
            model="o3-mini",
            messages=[
                {"role": "system", "content": "You are a PC building expert. Evaluate if the current build is suitable for the user's purpose. If upgrades are needed, recommend specific component upgrades with actual component IDs from the available options provided. If the build is already well-suited, indicate that no changes are necessary."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Add error handling for JSON parsing
        try:
            result = json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            # Handle case where the response isn't valid JSON
            logger.error("Failed to parse response as JSON")
            # Extract explanation from text response
            explanation_text = response.choices[0].message.content
            # Create a default result with just the explanation
            result = {
                "explanation": explanation_text,
                "components": {}  # Empty components dict means keep all existing components
            }
        
        # Create a single optimized build
        optimized_build = OptimizedBuildOut(
            id=1,
            name="Optimized Build",
            purpose=request.purpose,
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
