from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

# Component schemas
class CPUModel(BaseModel):
    id: int
    name: str
    brand: str
    socket: str | None
    cores: int
    threads: Optional[int]
    base_clock: Optional[float]
    cache: Optional[int]
    price: float

    class Config:
        from_attributes = True

class GPUModel(BaseModel):
    id: int
    name: str
    brand: Optional[str] = None
    model: Optional[str] = None
    memory: Optional[str] = None
    interface: Optional[str] = None
    base_clock: Optional[float] = None
    recommended_wattage: Optional[float] = None
    price: float

    class Config:
        from_attributes = True

class MotherboardModel(BaseModel):
    id: int
    name: str
    brand: str
    socket: str
    form_factor: str
    chipset: str
    memory_type: str
    price: float
    
    class Config:
        from_attributes = True

class RAMModel(BaseModel):
    id: int
    name: str
    brand: str | None
    type: str | None
    latency: str | None
    capacity: float | None
    speed: float | None
    memory_type: str | None
    price: float | None

    class Config:
        from_attributes = True

class PSUModel(BaseModel):
    id: int
    name: str
    brand: str | None
    wattage: int | None
    efficiency: str | None
    size: float | None
    color: str | None
    price: float | None

    class Config:
        from_attributes = True

class CaseModel(BaseModel):
    id: int
    name: str
    brand: str | None
    form_factor: str | None
    power_supply: str | None
    color: str | None
    additional_features: str | None
    price: float | None

    class Config:
        from_attributes = True

class StorageModel(BaseModel):
    id: int
    name: str
    type: str | None
    form_factor: str | None
    capacity: float | None
    interface: str | None
    rpm: float | None
    read_speed: float | None
    write_speed: float | None
    price: float | None

    class Config:
        from_attributes = True

class CoolerModel(BaseModel):
    id: int
    name: str
    brand: str | None
    type: str | None
    color: str | None
    size: float | None
    price: float | None

    class Config:
        from_attributes = True

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class UserRegisterSchema(BaseModel):
    email: str
    password: str
    model_config = ConfigDict(from_attributes=True)


class UserOutSchema(BaseModel):
    id: int
    email: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class SavedBuildCreate(BaseModel):
    name: str
    purpose: Optional[str] = None
    cpu_id: Optional[int] = None
    gpu_id: Optional[int] = None
    motherboard_id: Optional[int] = None
    ram_id: Optional[int] = None
    psu_id: Optional[int] = None
    case_id: Optional[int] = None
    storage_id: Optional[int] = None
    cooler_id: Optional[int] = None
    is_published: Optional[bool] = False

class SavedBuildOut(BaseModel):
    id: int
    name: str
    purpose: Optional[str] = None
    user_id: int
    cpu: Optional[CPUModel] = None
    gpu: Optional[GPUModel] = None
    motherboard: Optional[MotherboardModel] = None
    ram: Optional[RAMModel] = None
    psu: Optional[PSUModel] = None
    case: Optional[CaseModel] = None
    storage: Optional[StorageModel] = None
    cooler: Optional[CoolerModel] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class OptimizationRequest(BaseModel):
    purpose: str
    cpu_id: Optional[int] = None
    gpu_id: Optional[int] = None
    motherboard_id: Optional[int] = None
    ram_id: Optional[int] = None
    psu_id: Optional[int] = None
    case_id: Optional[int] = None
    storage_id: Optional[int] = None
    cooler_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class ComponentAnalysisItem(BaseModel):
    component_type: str
    message: str

class ComponentCompatibilityIssue(BaseModel):
    component_types: List[str]
    message: str

class ComponentAnalysis(BaseModel):
    analysis: List[Dict[str, Any]] = []
    missing_components: List[ComponentAnalysisItem] = []
    compatibility_issues: List[ComponentCompatibilityIssue] = []
    suggested_upgrades: List[ComponentAnalysisItem] = []

class OptimizedBuildOut(SavedBuildOut):
    explanation: str  # AI's explanation for the recommendations
    similarity_score: float  # ChromaDB similarity score
    component_analysis: Optional[ComponentAnalysis] = None  # New field for component analysis

    model_config = ConfigDict(from_attributes=True)

class BuildRatingCreate(BaseModel):
    rating: float  # 0-5 stars
    comment: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class BuildRatingOut(BaseModel):
    id: int
    published_build_id: int
    user_id: int
    rating: float
    comment: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PublishedBuildOut(BaseModel):
    id: int
    build: SavedBuildOut
    user_id: int
    avg_rating: float
    rating_count: int
    created_at: datetime
    ratings: list[BuildRatingOut] = []
    
    model_config = ConfigDict(from_attributes=True)

class PublicBuildResponse(BaseModel):
    builds: list[PublishedBuildOut]
    total: int
    
    model_config = ConfigDict(from_attributes=True) 