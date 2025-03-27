from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from core.deps import get_current_user
from schemas import OptimizationRequest, OptimizedBuildOut
from models import CPU, GPU, RAM, PSU, Case, Storage, Cooler, Motherboard
from typing import List, Dict, Any
import logging
import json
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
        
        # Initialize response components with the original IDs
        cpu_id = request.cpu_id
        gpu_id = request.gpu_id
        motherboard_id = request.motherboard_id
        ram_id = request.ram_id
        psu_id = request.psu_id
        case_id = request.case_id
        storage_id = request.storage_id
        cooler_id = request.cooler_id
        
        # Get purpose or use a default
        purpose = request.purpose or "general use"
        explanation = "No changes were made to your build."

        # Simple rule-based optimization logic
        if purpose and "gaming" in purpose.lower():
            if "4k" in purpose.lower():
                # For 4K gaming, recommend a high-end GPU
                high_end_gpus = db.query(GPU).filter(GPU.price > 5000).order_by(GPU.price.asc()).all()
                if high_end_gpus and (gpu_id is None or high_end_gpus[0].id != gpu_id):
                    gpu_id = high_end_gpus[0].id if high_end_gpus else gpu_id
                    explanation = f"Upgraded GPU to {high_end_gpus[0].name if high_end_gpus else 'a high-end GPU'} for optimal 4K gaming performance."
            else:
                # For regular gaming, recommend a mid-range GPU
                mid_range_gpus = db.query(GPU).filter(GPU.price.between(3000, 5000)).order_by(GPU.price.desc()).all()
                if mid_range_gpus and (gpu_id is None or mid_range_gpus[0].id != gpu_id):
                    gpu_id = mid_range_gpus[0].id if mid_range_gpus else gpu_id
                    explanation = f"Recommended {mid_range_gpus[0].name if mid_range_gpus else 'a mid-range GPU'} for balanced gaming performance."
        
        elif purpose and any(x in purpose.lower() for x in ["video", "editing", "rendering", "3d"]):
            # For content creation, recommend a high-core CPU and more RAM
            high_core_cpus = db.query(CPU).filter(CPU.cores >= 8).order_by(CPU.cores.desc()).all()
            if high_core_cpus and (cpu_id is None or high_core_cpus[0].id != cpu_id):
                cpu_id = high_core_cpus[0].id if high_core_cpus else cpu_id
                explanation = f"Upgraded CPU to {high_core_cpus[0].name if high_core_cpus else 'a high-core CPU'} for better content creation performance."
        
        return OptimizedBuildOut(
            id=1,
            name="Optimized Build",
            purpose=purpose,
            user_id=current_user.id,
            cpu_id=cpu_id,
            gpu_id=gpu_id,
            motherboard_id=motherboard_id,
            ram_id=ram_id,
            psu_id=psu_id,
            case_id=case_id,
            storage_id=storage_id,
            cooler_id=cooler_id,
            explanation=explanation,
            similarity_score=0.95,
            created_at=current_time,
            updated_at=current_time
        )
        
    except Exception as e:
        error_msg = f"Error in optimize_build: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=error_msg
        )
