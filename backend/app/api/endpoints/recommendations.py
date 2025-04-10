from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from database import get_db
from .auth import oauth2_scheme, get_current_user
import logging
from models import CPU, GPU, Motherboard, RAM, Storage, PSU, Cooler, Case
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)

class ComponentRecommendation(BaseModel):
    component_type: str
    message: str
    suggested_component_id: Optional[int] = None

class RecommendationResponse(BaseModel):
    suggestions: List[ComponentRecommendation]

class BuildComponentInfo(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    price: Optional[str] = None
    socket: Optional[str] = None
    form_factor: Optional[str] = None
    wattage: Optional[int] = None
    capacity: Optional[str] = None
    vram: Optional[str] = None

class RecommendationRequest(BaseModel):
    cpu: Optional[BuildComponentInfo] = None
    gpu: Optional[BuildComponentInfo] = None
    motherboard: Optional[BuildComponentInfo] = None
    ram: Optional[BuildComponentInfo] = None
    psu: Optional[BuildComponentInfo] = None
    case: Optional[BuildComponentInfo] = None
    storage: Optional[BuildComponentInfo] = None
    cooler: Optional[BuildComponentInfo] = None
    purpose: Optional[str] = None

@router.post("", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze the current build and provide AI recommendations for improvements
    based on compatibility, performance needs, and budget considerations.
    """
    logger.info(f"Recommendation request received for build with purpose: {request.purpose}")
    
    recommendations = []
    
    try:
        # Check for basic component presence
        if not request.cpu:
            recommendations.append(ComponentRecommendation(
                component_type="cpu",
                message="En processor (CPU) är nödvändig för alla datorer. Välj en baserad på ditt användningsområde."
            ))
        
        if not request.motherboard:
            recommendations.append(ComponentRecommendation(
                component_type="motherboard",
                message="Välj ett moderkort som är kompatibelt med din processor (samma socket-typ)."
            ))
        
        if not request.ram:
            recommendations.append(ComponentRecommendation(
                component_type="ram",
                message="Minne (RAM) behövs för alla datorer. För moderna system rekommenderas minst 16GB."
            ))
            
        if not request.psu:
            recommendations.append(ComponentRecommendation(
                component_type="psu",
                message="Ett nätaggregat behövs för att driva datorn. Säkerställ att det har tillräcklig effekt för alla komponenter."
            ))
        
        # CPU-GPU balance check for gaming
        if request.purpose and "gaming" in request.purpose.lower():
            if request.cpu and request.gpu:
                cpu_price = int(request.cpu.price.replace(' kr', '').replace(' ', '')) if isinstance(request.cpu.price, str) else int(request.cpu.price or 0)
                gpu_price = int(request.gpu.price.replace(' kr', '').replace(' ', '')) if isinstance(request.gpu.price, str) else int(request.gpu.price or 0)
                
                # For gaming, GPU should generally be more expensive than CPU
                if cpu_price > gpu_price * 1.5:
                    recommendations.append(ComponentRecommendation(
                        component_type="gpu",
                        message=f"För gaming rekommenderas att spendera mer på grafikkortet än på processorn. Överväg att uppgradera ditt grafikkort eller välja en billigare processor."
                    ))
                    
            # Check VRAM for gaming at different resolutions
            if request.gpu and request.gpu.vram:
                vram = int(request.gpu.vram.replace('GB', '').strip()) if isinstance(request.gpu.vram, str) else request.gpu.vram
                
                if "4k" in request.purpose.lower() and vram < 8:
                    recommendations.append(ComponentRecommendation(
                        component_type="gpu",
                        message=f"För 4K-gaming rekommenderas ett grafikkort med minst 8GB VRAM. Ditt nuvarande kort har endast {vram}GB."
                    ))
                elif "1440p" in request.purpose.lower() and vram < 6:
                    recommendations.append(ComponentRecommendation(
                        component_type="gpu",
                        message=f"För 1440p-gaming rekommenderas ett grafikkort med minst 6GB VRAM. Ditt nuvarande kort har endast {vram}GB."
                    ))
        
        # Check PSU wattage if GPU is present
        if request.gpu and request.psu:
            # Estimate system power consumption (simplified)
            estimated_power = 150  # Base system
            if request.cpu:
                estimated_power += 100  # Typical CPU
            
            gpu_power = 0
            if hasattr(request.gpu, 'power_consumption') and request.gpu.power_consumption:
                gpu_power = int(request.gpu.power_consumption)
            else:
                # Approximate based on VRAM if available
                if request.gpu.vram:
                    vram = int(request.gpu.vram.replace('GB', '').strip()) if isinstance(request.gpu.vram, str) else request.gpu.vram
                    gpu_power = 75 + (vram * 20)  # Rough estimate
            
            estimated_power += gpu_power
            
            # Add 20% headroom
            recommended_power = estimated_power * 1.2
            
            psu_wattage = int(request.psu.wattage) if request.psu.wattage else 0
            
            if psu_wattage < recommended_power:
                recommendations.append(ComponentRecommendation(
                    component_type="psu",
                    message=f"Ditt nätaggregat på {psu_wattage}W kan vara för svagt för ditt system. Vi rekommenderar minst {int(recommended_power)}W."
                ))
        
        # Check for SSD storage
        if request.storage and request.storage.name:
            if "ssd" not in request.storage.name.lower() and "nvme" not in request.storage.name.lower():
                recommendations.append(ComponentRecommendation(
                    component_type="storage",
                    message="För bättre systemprestandabör du använda en SSD för operativsystemet och program. En traditionell hårddisk (HDD) kan användas för lagring av data."
                ))
        
        # Check RAM capacity for purpose
        if request.ram and request.ram.capacity and request.purpose:
            ram_capacity = 0
            if isinstance(request.ram.capacity, str):
                # Extract numeric part from strings like "16GB"
                ram_capacity = int(''.join(filter(str.isdigit, request.ram.capacity)))
            else:
                ram_capacity = request.ram.capacity
                
            if ("utveckla" in request.purpose.lower() or "programmera" in request.purpose.lower()) and ram_capacity < 16:
                recommendations.append(ComponentRecommendation(
                    component_type="ram",
                    message=f"För utvecklingsmiljöer rekommenderas minst 16GB RAM. Ditt nuvarande val har endast {ram_capacity}GB."
                ))
            elif "machine learning" in request.purpose.lower() and ram_capacity < 32:
                recommendations.append(ComponentRecommendation(
                    component_type="ram",
                    message=f"För AI och Machine Learning rekommenderas minst 32GB RAM. Ditt nuvarande val har endast {ram_capacity}GB."
                ))
            elif "video" in request.purpose.lower() and ram_capacity < 32:
                recommendations.append(ComponentRecommendation(
                    component_type="ram",
                    message=f"För videoredigering rekommenderas minst 32GB RAM. Ditt nuvarande val har endast {ram_capacity}GB."
                ))
        
        # CPU cooling recommendations
        if request.cpu and not request.cooler:
            recommendations.append(ComponentRecommendation(
                component_type="cpu-cooler",
                message="En CPU-kylare rekommenderas för optimal prestanda och livslängd på din processor."
            ))
        
        # If no specific issues found but components are missing
        if not recommendations and len([c for c in [request.cpu, request.gpu, request.motherboard, request.ram, request.psu, request.case, request.storage] if c]) < 5:
            recommendations.append(ComponentRecommendation(
                component_type="general",
                message="Din dator är ofullständig. Fortsätt lägga till komponenter för en komplett dator."
            ))
            
        # If build seems complete but no issues found
        if not recommendations and len([c for c in [request.cpu, request.gpu, request.motherboard, request.ram, request.psu, request.case, request.storage] if c]) >= 5:
            recommendations.append(ComponentRecommendation(
                component_type="general",
                message="Din dator verkar vara väl balanserad och komplett! Alla viktiga komponenter är valda och kompatibla med varandra."
            ))
            
        return RecommendationResponse(suggestions=recommendations)
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Could not generate recommendations: {str(e)}"
        ) 