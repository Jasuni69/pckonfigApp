from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import CPU, GPU, Motherboard, RAM, Storage, PSU, Cooler, Case, SavedBuild, Token, User, PublishedBuild, BuildRating
from schemas import CPUModel, GPUModel, MotherboardModel, RAMModel, StorageModel, PSUModel, CoolerModel, CaseModel, SavedBuildCreate, SavedBuildOut, PublicBuildResponse, BuildRatingCreate, BuildRatingOut
from .auth import oauth2_scheme
from typing import Optional

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
        db_token = db.query(Token).filter(Token.token == token).first()
        if not db_token:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(User).filter(User.id == db_token.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        new_build = SavedBuild(
            name=build.name,
            purpose=build.purpose,
            user_id=user.id, 
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

        db_token = db.query(Token).filter(Token.token == token).first()
        if not db_token:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(User).filter(User.id == db_token.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        builds = db.query(SavedBuild).filter(SavedBuild.user_id == user.id).all()
        return builds
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Det gick inte att hämta sparade datorer: {str(e)}"
        )

@router.delete("/builds/{build_id}", response_model=dict)
async def delete_build(
    build_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        # Validate token and get user
        db_token = db.query(Token).filter(Token.token == token).first()
        if not db_token:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(User).filter(User.id == db_token.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Find the build
        build = db.query(SavedBuild).filter(SavedBuild.id == build_id).first()
        if not build:
            raise HTTPException(status_code=404, detail="Build not found")

        # Check if the build belongs to the user
        if build.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this build")

        # Delete the build
        db.delete(build)
        db.commit()
        
        return {"message": "Build deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Det gick inte att ta bort datorn: {str(e)}"
        )

@router.get("/builds/public", response_model=PublicBuildResponse)
async def get_published_builds(
    skip: int = 0,
    limit: int = 20,
    purpose: Optional[str] = None,
    cpu_id: Optional[int] = None,
    gpu_id: Optional[int] = None,
    case_id: Optional[int] = None,
    ram_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(PublishedBuild).join(SavedBuild)
        
        # Apply filters if provided
        if purpose:
            query = query.filter(SavedBuild.purpose == purpose)
        if cpu_id:
            query = query.filter(SavedBuild.cpu_id == cpu_id)
        if gpu_id:
            query = query.filter(SavedBuild.gpu_id == gpu_id)
        if case_id:
            query = query.filter(SavedBuild.case_id == case_id)
        if ram_id:
            query = query.filter(SavedBuild.ram_id == ram_id)
            
        # Get total count
        total = query.count()
        
        # Apply pagination
        builds = query.order_by(PublishedBuild.created_at.desc()).offset(skip).limit(limit).all()
        
        return {"builds": builds, "total": total}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Det gick inte att hämta publicerade datorer: {str(e)}"
        )

@router.post("/builds/{build_id}/publish", response_model=dict)
async def publish_build(
    build_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        # Validate token and get user
        db_token = db.query(Token).filter(Token.token == token).first()
        if not db_token:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(User).filter(User.id == db_token.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Find the build
        build = db.query(SavedBuild).filter(SavedBuild.id == build_id).first()
        if not build:
            raise HTTPException(status_code=404, detail="Build not found")

        # Check if the build belongs to the user
        if build.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to publish this build")
            
        # Check if already published
        if build.is_published:
            return {"message": "Build is already published"}

        # Mark the build as published
        build.is_published = True
        
        # Create a new published build entry
        published_build = PublishedBuild(
            build_id=build.id,
            user_id=user.id
        )
        
        db.add(published_build)
        db.commit()
        
        return {"message": "Build published successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Det gick inte att publicera datorn: {str(e)}"
        )

@router.post("/builds/public/{published_build_id}/rate", response_model=BuildRatingOut)
async def rate_build(
    published_build_id: int,
    rating_data: BuildRatingCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        # Validate token and get user
        db_token = db.query(Token).filter(Token.token == token).first()
        if not db_token:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(User).filter(User.id == db_token.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if published build exists
        published_build = db.query(PublishedBuild).filter(PublishedBuild.id == published_build_id).first()
        if not published_build:
            raise HTTPException(status_code=404, detail="Published build not found")
            
        # Validate rating is between 0 and 5
        if rating_data.rating < 0 or rating_data.rating > 5:
            raise HTTPException(status_code=400, detail="Rating must be between 0 and 5")

        # Check if user has already rated this build
        existing_rating = db.query(BuildRating).filter(
            BuildRating.published_build_id == published_build_id,
            BuildRating.user_id == user.id
        ).first()
        
        if existing_rating:
            # Update existing rating
            old_rating = existing_rating.rating
            existing_rating.rating = rating_data.rating
            existing_rating.comment = rating_data.comment
            
            # Update average rating
            total_rating = (published_build.avg_rating * published_build.rating_count) - old_rating + rating_data.rating
            published_build.avg_rating = total_rating / published_build.rating_count
            
            db.commit()
            db.refresh(existing_rating)
            return existing_rating
        else:
            # Create new rating
            new_rating = BuildRating(
                published_build_id=published_build_id,
                user_id=user.id,
                rating=rating_data.rating,
                comment=rating_data.comment
            )
            db.add(new_rating)
            
            # Update build's average rating
            total_rating = (published_build.avg_rating * published_build.rating_count) + rating_data.rating
            published_build.rating_count += 1
            published_build.avg_rating = total_rating / published_build.rating_count
            
            db.commit()
            db.refresh(new_rating)
            return new_rating
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Det gick inte att betygsätta bygget: {str(e)}"
        )

@router.get("/builds/public/{published_build_id}/ratings", response_model=list[BuildRatingOut])
async def get_build_ratings(
    published_build_id: int,
    db: Session = Depends(get_db)
):
    try:
        # Check if published build exists
        published_build = db.query(PublishedBuild).filter(PublishedBuild.id == published_build_id).first()
        if not published_build:
            raise HTTPException(status_code=404, detail="Published build not found")
            
        ratings = db.query(BuildRating).filter(
            BuildRating.published_build_id == published_build_id
        ).order_by(BuildRating.created_at.desc()).all()
        
        return ratings
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Det gick inte att hämta betyg: {str(e)}"
        )