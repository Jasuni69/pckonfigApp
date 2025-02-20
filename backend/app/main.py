from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import verify_password, get_password_hash
from app.models import User
from app.database import get_db

app = FastAPI()

class CPUModel(BaseModel):
    id: int
    name: str
    brand: str
    socket: str
    cores: int
    threads: int
    base_clock: float
    cache: float
    price: float

    class Config:
        from_attributes = True  # Fixes serialization issue

@app.get("/cpus", response_model=list[CPUModel])
def get_cpus(db: Session = Depends(get_db)):
    return db.query(CPU).all()
