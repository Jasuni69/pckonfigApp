from fastapi import APIRouter, Depends, HTTPException
from app.deps import get_current_user, get_db
from ChromaDB.manager import search_components
from app.schemas import OptimizationRequest, OptimizedBuildOut
from sqlalchemy.orm import Session
from typing import List
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/optimize-build", response_model=List[OptimizedBuildOut])
async def optimize_build(
    request: OptimizationRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        purpose = request.purpose
        logger.info(f"Optimizing build for purpose: {purpose}")
        
        query = f"""
        Recommend components for {purpose} PC build.
        Current components and requirements:
        CPU ID: {request.cpu_id}
        GPU ID: {request.gpu_id} (Consider power requirements)
        Motherboard ID: {request.motherboard_id} (Check socket and form factor)
        RAM ID: {request.ram_id} (Focus on sufficient capacity for {purpose})
        PSU ID: {request.psu_id} (Ensure adequate wattage for system)
        Case ID: {request.case_id} (Check form factor compatibility)
        Storage ID: {request.storage_id}
        Cooler ID: {request.cooler_id}
        
        Consider:
        1. Total system power needs
        2. RAM capacity for {purpose} usage
        3. Case compatibility
        4. Overall system balance
        """
        
        logger.info("Querying ChromaDB for recommendations")
        results = search_components(query, n_results=3)
        logger.info(f"Received {len(results['documents'][0])} recommendations from ChromaDB")
        
        optimized_builds = []
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            logger.debug(f"Processing recommendation {i+1}: {doc[:100]}...")
            
            build = OptimizedBuildOut(
                id=i,
                name=f"Optimized Build {i+1}",
                purpose=purpose,
                user_id=current_user.id,
                explanation=doc,
                similarity_score=results['distances'][0][i] if 'distances' in results else 0.0,
                cpu_id=metadata.get("cpu_id"),
                gpu_id=metadata.get("gpu_id"),
                motherboard_id=metadata.get("motherboard_id"),
                ram_id=metadata.get("ram_id"),
                psu_id=metadata.get("psu_id"),
                case_id=metadata.get("case_id"),
                storage_id=metadata.get("storage_id"),
                cooler_id=metadata.get("cooler_id")
            )
            optimized_builds.append(build)
        
        logger.info(f"Returning {len(optimized_builds)} optimized builds")
        return optimized_builds
        
    except Exception as e:
        logger.error(f"Error in optimize_build: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error optimizing build: {str(e)}"
        )
