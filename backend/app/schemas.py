from pydantic import BaseModel, EmailStr
from typing import Optional

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