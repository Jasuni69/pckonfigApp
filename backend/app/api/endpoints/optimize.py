from fastapi import APIRouter, Depends, HTTPException
from app.deps import get_current_user, get_db
from ChromaDB.manager import search_components
from app.schemas import OptimizationRequest, OptimizedBuildOut
from sqlalchemy.orm import Session
from typing import List
import logging
import json
import openai

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/optimize-build", response_model=OptimizedBuildOut)
async def optimize_build(
    request: OptimizationRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Get current component details
        current_components = {}
        
        if request.cpu_id:
            current_components["cpu"] = db.query(CPU).filter(CPU.id == request.cpu_id).first()
        # Get other components the same way...
        
        # Get all available components
        all_cpus = [{"id": c.id, "name": c.name, "socket": c.socket, "cores": c.cores, "price": c.price} 
                   for c in db.query(CPU).all()]
        # Get other component types similarly...
        
        # Ask AI to optimize the build
        prompt = f"""
        Analyze this PC build for {request.purpose}:
        
        Current components:
        {json.dumps(current_components, indent=2)}
        
        Based on the purpose "{request.purpose}", identify components that need upgrading.
        Only suggest changes that are necessary - keep components that are already suitable.
        
        Return a single optimized build with:
        1. Which components to keep
        2. Which components to replace and why
        3. A brief explanation of the changes
        
        Format as JSON:
        {{
          "explanation": "Overall explanation of changes",
          "changes": [
            {{ "component": "gpu", "from_id": 123, "to_id": 456, "reason": "The 4060 is not powerful enough for 4K gaming" }}
          ],
          "components": {{
            "cpu_id": 1,
            "gpu_id": 2,
            // other component IDs
          }}
        }}
        """
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a PC building expert. Identify components that need upgrading based on the user's purpose."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
        )
        
        result = json.loads(response.choices[0].message.content)
        
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
            similarity_score=0.95
        )
        
        return optimized_build
        
    except Exception as e:
        logger.error(f"Error in optimize_build: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error optimizing build: {str(e)}"
        )
