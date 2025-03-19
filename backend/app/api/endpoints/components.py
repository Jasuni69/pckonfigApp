from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import CPU, GPU, Motherboard, RAM, Storage, PSU, Cooler, Case, SavedBuild, Token, User
from schemas import CPUModel, GPUModel, MotherboardModel, RAMModel, StorageModel, PSUModel, CoolerModel, CaseModel, SavedBuildCreate, SavedBuildOut
from .auth import oauth2_scheme

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

@router.post("/builds", response_model=SavedBuildOut)
async def save_build(
    build: SavedBuildCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        # Get the user from the token
        db_token = db.query(Token).filter(Token.token == token).first()
        if not db_token:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get the user
        user = db.query(User).filter(User.id == db_token.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create new build associated with the user
        new_build = SavedBuild(
            name=build.name,
            user_id=user.id,  # Associate with user ID
            cpu_id=build.cpu_id,
            gpu_id=build.gpu_id,
            motherboard_id=build.motherboard_id,
            ram_id=build.ram_id,
            psu_id=build.psu_id,
            case_id=build.case_id,
            storage_id=build.storage_id,
            cooler_id=build.cooler_id
        )
        
        db.add(new_build)
        db.commit()
        db.refresh(new_build)
        
        return new_build
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Det gick inte att spara datorn: {str(e)}"
        )

@router.get("/builds", response_model=list[SavedBuildOut])
async def get_user_builds(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        # Get the user from the token
        db_token = db.query(Token).filter(Token.token == token).first()
        if not db_token:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Get the user
        user = db.query(User).filter(User.id == db_token.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get all builds for the user by user ID
        builds = db.query(SavedBuild).filter(SavedBuild.user_id == user.id).all()
        return builds
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Det gick inte att hämta sparade datorer: {str(e)}"
        )