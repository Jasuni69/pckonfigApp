from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import CPU
from pydantic import BaseModel

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
