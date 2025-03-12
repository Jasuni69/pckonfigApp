from datetime import UTC, datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.security import get_password_hash, verify_password
from app.schemas import UserRegisterSchema, UserOutSchema
from app.database import get_db
from app.models import User, Token
from app.core import settings
import base64
from random import SystemRandom

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
_sysrand = SystemRandom()

def token_urlsafe(nbytes=32):
    tok = _sysrand.randbytes(nbytes)
    return base64.urlsafe_b64encode(tok).rstrip(b"=").decode("ascii")

def create_database_token(user_id: int, db: Session):
    randomized_token = token_urlsafe()
    new_token = Token(token=randomized_token, user_id=user_id)
    db.add(new_token)
    db.commit()
    return new_token

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

@router.post("/login")
async def login(email: str, password: str, db: Session = Depends(get_db)):
    try:
        # Find user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Felaktig email eller lösenord"
            )
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Felaktig email eller lösenord"
            )
        
        # Create token
        token = create_database_token(user.id, db)
        
        return {
            "access_token": token.token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ett fel uppstod vid inloggning: {str(e)}"
        )

@router.get("/me", response_model=UserOutSchema)
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        # Verify token
        max_age = timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        db_token = db.query(Token).filter(
            Token.token == token,
            Token.created_at >= datetime.now(UTC) - max_age
        ).first()
        
        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalid or expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return db_token.user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
