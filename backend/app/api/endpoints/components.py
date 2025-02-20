from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import CPU, GPU, Motherboard, RAM, Storage, PSU, Cooler, Case
from schemas import CPUModel, GPUModel, MotherboardModel, RAMModel, StorageModel, PSUModel, CoolerModel, CaseModel

router = APIRouter()

@router.get("/cpus", response_model=list[CPUModel])
def get_cpus(db: Session = Depends(get_db)):
    return db.query(CPU).all()

@router.get("/gpus", response_model=list[GPUModel])
def get_gpus(db: Session = Depends(get_db)):
    return db.query(GPU).all()

@router.get("/motherboards", response_model=list[MotherboardModel])
def get_motherboards(db: Session = Depends(get_db)):
    return db.query(Motherboard).all()

@router.get("/ram", response_model=list[RAMModel])
def get_rams(db: Session = Depends(get_db)):
    return db.query(RAM).all()

@router.get("/storage", response_model=list[StorageModel])
def get_storages(db: Session = Depends(get_db)):
    return db.query(Storage).all()

@router.get("/psus", response_model=list[PSUModel])
def get_psus(db: Session = Depends(get_db)):
    return db.query(PSU).all()

@router.get("/coolers", response_model=list[CoolerModel])
def get_coolers(db: Session = Depends(get_db)):
    return db.query(Cooler).all()

@router.get("/cases", response_model=list[CaseModel])
def get_cases(db: Session = Depends(get_db)):
    return db.query(Case).all()