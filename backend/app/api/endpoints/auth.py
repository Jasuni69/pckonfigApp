from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.schemas import UserRegisterSchema, UserOutSchema
from app.database import get_db
from app.models import User
from datetime import datetime

router = APIRouter()

@router.post("/register", response_model=UserOutSchema)
async def register_user(user: UserRegisterSchema, db: Session = Depends(get_db)):
    try:
      
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(
                status_code=400, 
                detail="Email är redan registrerad"
            )
        
        
        db_user = User(
            email=user.email,
            hashed_password=get_password_hash(user.password),  
            created_at=datetime.utcnow()
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Ett fel uppstod vid registrering: {str(e)}"
        )
