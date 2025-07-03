from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from core.deps import get_current_user
from schemas import OptimizationRequest, OptimizedBuildOut, ComponentAnalysis
from models import CPU, GPU, RAM, PSU, Case, Storage, Cooler, Motherboard
from ChromaDB.manager import search_components, search_components_by_type
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

class BuildOptimizer:
    """Separate class to handle build optimization logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.max_components = 3
    
    def extract_gb(self, memory_str: str) -> Optional[float]:
        """Extract gigabyte value from memory strings like '12GB', '8 GB', etc."""
        if not memory_str or not isinstance(memory_str, str):
            return None
        
        match = re.search(r"(\d+(?:\.\d+)?)\s*gb", memory_str.lower())
        if match:
            return float(match.group(1))
        return None
    
    def get_current_components(self, request: OptimizationRequest) -> Dict[str, Any]:
        """Extract and format current component details from request"""
        current_components = {}
        
        # Extract CPU details
        if request.cpu_id:
            cpu = self.db.query(CPU).filter(CPU.id == request.cpu_id).first()
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
            gpu = self.db.query(GPU).filter(GPU.id == request.gpu_id).first()
            if gpu:
                current_components["gpu"] = {
                    "id": gpu.id,
                    "name": gpu.name,
                    "memory": getattr(gpu, 'memory', None),
                    "recommended_wattage": getattr(gpu, 'recommended_wattage', None),
                    "price": gpu.price
                }
        
        # Add other components similarly...
        # (Motherboard, RAM, PSU, Case, Storage, Cooler)
        
        return current_components
    
    def analyze_build_compatibility(self, components: Dict[str, Any], purpose: str) -> Dict[str, Any]:
        """Analyze build for compatibility issues and suggestions"""
        component_analysis = {
            "analysis": [],
            "missing_components": [],
            "compatibility_issues": [],
            "suggested_upgrades": []
        }
        
        # Check missing essential components
        essential_components = ["cpu", "motherboard", "ram", "psu", "storage"]
        for comp in essential_components:
            if comp not in components:
                component_analysis["missing_components"].append({
                    "component_type": comp,
                    "message": f"Din dator saknar {comp}"
                })
        
        # Check RAM sufficiency for purpose
        self._check_ram_requirements(components, purpose, component_analysis)
        
        # Check GPU VRAM for 4K gaming
        self._check_gpu_vram_requirements(components, purpose, component_analysis)
        
        return component_analysis
    
    def _check_ram_requirements(self, components: Dict[str, Any], purpose: str, analysis: Dict[str, Any]):
        """Check if RAM is sufficient for the intended purpose"""
        if "ram" not in components:
            return
            
        purpose_lower = purpose.lower()
        ram_capacity = 0
        
        if components["ram"].get("capacity"):
            try:
                ram_capacity = float(components["ram"]["capacity"])
            except (ValueError, TypeError):
                ram_str = str(components["ram"]["capacity"])
                ram_match = re.search(r"(\d+(?:\.\d+)?)", ram_str)
                if ram_match:
                    ram_capacity = float(ram_match.group(1))
        
        needed_ram = self._get_recommended_ram_for_purpose(purpose_lower)
        
        if ram_capacity < needed_ram:
            analysis["suggested_upgrades"].append({
                "component_type": "ram",
                "message": f"För '{purpose}' rekommenderas minst {int(needed_ram)}GB RAM. Du har {int(ram_capacity)}GB."
            })
    
    def _get_recommended_ram_for_purpose(self, purpose_lower: str) -> int:
        """Get recommended RAM amount based on purpose"""
        if "gaming" in purpose_lower:
            if "4k" in purpose_lower:
                return 32
            else:
                return 16
        elif any(p in purpose_lower for p in ["utveckling", "development", "programmering", "coding"]):
            return 16
        elif any(p in purpose_lower for p in ["video", "editing", "redigering", "rendering"]):
            return 32
        elif any(p in purpose_lower for p in ["ai", "machine learning", "deep learning"]):
            return 32
        return 8  # Default minimal RAM
    
    def _check_gpu_vram_requirements(self, components: Dict[str, Any], purpose: str, analysis: Dict[str, Any]):
        """Check GPU VRAM requirements for gaming"""
        if "gaming" not in purpose.lower() or "gpu" not in components:
            return
            
        purpose_lower = purpose.lower()
        gpu_vram = self.extract_gb(components["gpu"].get("memory", ""))
        
        if "4k" in purpose_lower and gpu_vram is not None and gpu_vram < 12:
            if gpu_vram < 8:
                message = f"För 4K-gaming är 8GB VRAM minimum, men ditt kort har endast {int(gpu_vram)}GB. För optimal 4K-upplevelse rekommenderas 12GB+ VRAM."
            else:
                message = f"För optimal 4K-gaming rekommenderas ett grafikkort med minst 12GB VRAM för bästa prestanda. Ditt kort har {int(gpu_vram)}GB."
            
            analysis["suggested_upgrades"].append({
                "component_type": "gpu",
                "message": message
            })

@router.post("/build", response_model=OptimizedBuildOut)
async def optimize_build(
    request: OptimizationRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        logger.info("Received optimization request for purpose: %s", request.purpose)
        
        # Initialize optimizer
        optimizer = BuildOptimizer(db)
        
        # Get current components
        current_components = optimizer.get_current_components(request)
        
        # Analyze compatibility and requirements
        purpose = request.purpose or "general use"
        component_analysis = optimizer.analyze_build_compatibility(current_components, purpose)
        
        # Get AI recommendations with improved diversity
        recommendations = await get_component_recommendations(purpose, current_components, db)
        
        # Generate AI explanation
        explanation = await generate_optimization_explanation(
            current_components, recommendations, purpose, component_analysis
        )
        
        return {
            "status": "success",
            "explanation": explanation,
            "component_analysis": component_analysis,
            "recommended_components": recommendations,
            "total_price": calculate_total_price(recommendations)
        }
        
    except Exception as e:
        logger.error(f"Error in optimize_build: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "message": "An error occurred while optimizing the build."
        }

async def get_component_recommendations(purpose: str, current_components: Dict, db: Session) -> Dict[str, List]:
    """Get component recommendations using ChromaDB with diversity controls"""
    recommendations = {}
    max_components = 3
    
    # Get current component IDs to exclude from recommendations
    exclude_ids = set()
    for comp_data in current_components.values():
        if isinstance(comp_data, dict) and "id" in comp_data:
            exclude_ids.add(str(comp_data["id"]))
    
    # Define component types and their mapping to ChromaDB types
    component_mappings = {
        "cpus": "CPU",
        "gpus": "GPU", 
        "motherboards": "Motherboard",
        "ram": "RAM",
        "psus": "PSU",
        "cases": "Case",
        "storage": "Storage",
        "coolers": "Cooler"
    }
    
    # Determine budget range based on current components
    current_prices = [comp.get("price", 0) for comp in current_components.values() if isinstance(comp, dict)]
    if current_prices:
        avg_price = sum(current_prices) / len(current_prices)
        budget_range = (max(500, avg_price * 0.5), avg_price * 2.0)
    else:
        budget_range = None
    
    # Search for each component type
    for component_key, chroma_type in component_mappings.items():
        try:
            logger.info(f"Searching for {component_key} with purpose: {purpose}")
            
            # Use type-specific search with diversity
            results = search_components_by_type(
                component_type=chroma_type,
                purpose=purpose,
                n_results=max_components,
                exclude_ids=exclude_ids,
                budget_range=budget_range
            )
            
            # Convert ChromaDB results to API format
            component_list = []
            if results.get("metadatas") and results["metadatas"][0]:
                for i, metadata in enumerate(results["metadatas"][0]):
                    component = {
                        "id": metadata.get("id"),
                        "name": metadata.get("name"),
                        "brand": metadata.get("brand"),
                        "price": metadata.get("price"),
                        "type": metadata.get("type"),
                        "similarity_score": 1.0 - results["distances"][0][i] if results.get("distances") else 0.5
                    }
                    
                    # Add type-specific fields
                    if chroma_type == "CPU":
                        component.update({
                            "socket": metadata.get("socket"),
                            "cores": metadata.get("cores"),
                            "threads": metadata.get("threads"),
                            "base_clock": metadata.get("base_clock")
                        })
                    elif chroma_type == "GPU":
                        component.update({
                            "memory": metadata.get("memory"),
                            "recommended_wattage": metadata.get("recommended_wattage")
                        })
                    elif chroma_type == "RAM":
                        component.update({
                            "capacity": metadata.get("capacity"),
                            "speed": metadata.get("speed"),
                            "memory_type": metadata.get("memory_type")
                        })
                    elif chroma_type == "Motherboard":
                        component.update({
                            "socket": metadata.get("socket"),
                            "form_factor": metadata.get("form_factor"),
                            "chipset": metadata.get("chipset")
                        })
                    
                    component_list.append(component)
            
            recommendations[component_key] = component_list
            logger.info(f"Found {len(component_list)} recommendations for {component_key}")
            
        except Exception as e:
            logger.error(f"Error searching for {component_key}: {str(e)}")
            recommendations[component_key] = []
    
    return recommendations

async def generate_optimization_explanation(
    current: Dict, recommendations: Dict, purpose: str, analysis: Dict
) -> str:
    """Generate AI explanation for the optimization"""
    # Count total recommendations
    total_recommendations = sum(len(comps) for comps in recommendations.values())
    
    # Create base explanation
    explanation = f"Optimering för {purpose} slutförd med förbättrad mångfald i rekommendationer. "
    
    if total_recommendations > 0:
        explanation += f"Hittade {total_recommendations} olika komponenter från olika tillverkare och prisklasser för att ge dig fler valmöjligheter. "
        
        # Add analysis insights
        if analysis.get("missing_components"):
            explanation += f"Identifierade {len(analysis['missing_components'])} saknade komponenter. "
        
        if analysis.get("suggested_upgrades"):
            explanation += f"Föreslår {len(analysis['suggested_upgrades'])} uppgraderingar baserat på ditt användningsområde. "
        
        explanation += "Rekommendationerna är optimerade för att undvika upprepning och ge dig varierade alternativ."
    else:
        explanation += "Inga specifika rekommendationer hittades för din konfiguration."
    
    return explanation

def calculate_total_price(recommendations: Dict[str, List]) -> int:
    """Calculate total price of recommended components"""
    total = 0
    for component_list in recommendations.values():
        if component_list and isinstance(component_list, list):
            for comp in component_list:
                total += comp.get('price', 0) or 0
    return total