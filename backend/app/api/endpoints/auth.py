from datetime import UTC, datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from core.security import get_password_hash, verify_password, validate_password_strength
from schemas import UserRegisterSchema, UserOutSchema
from database import get_db
from models import User, Token
from core import settings
import base64
from random import SystemRandom
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
_sysrand = SystemRandom()
limiter = Limiter(key_func=get_remote_address)

def token_urlsafe(nbytes=32):
    tok = _sysrand.randbytes(nbytes)
    return base64.urlsafe_b64encode(tok).rstrip(b"=").decode("ascii")

def create_database_token(user_id: int, db: Session):
    randomized_token = token_urlsafe()
    new_token = Token(token=randomized_token, user_id=user_id)
    db.add(new_token)
    db.commit()
    return new_token

class LoginData(BaseModel):
    email: str
    password: str

@router.post("/register", response_model=UserOutSchema)
@limiter.limit("5/minute")  # Limit registration attempts
async def register_user(request: Request, user: UserRegisterSchema, db: Session = Depends(get_db)):
    try:
        # Validate password strength
        password_validation = validate_password_strength(user.password)
        if not password_validation["is_valid"]:
            raise HTTPException(
                status_code=400,
                detail=f"Lösenord uppfyller inte kraven: {', '.join(password_validation['errors'])}"
            )
      
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
@limiter.limit("10/minute")  # Limit login attempts
async def login(request: Request, login_data: LoginData, db: Session = Depends(get_db)):
    try:
        # Find user
        user = db.query(User).filter(User.email == login_data.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Felaktig email eller lösenord"
            )
        
        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
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
            Token.created >= datetime.now(UTC) - max_age
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

@router.post("/refresh-token")
async def refresh_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        # Find the existing token
        max_age = timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        db_token = db.query(Token).filter(
            Token.token == token,
            Token.created >= datetime.now(UTC) - max_age
        ).first()
        
        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalid or expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Update token timestamp
        db_token.created = datetime.now(UTC)
        db.commit()
        db.refresh(db_token)
        
        return {
            "access_token": db_token.token,
            "token_type": "bearer",
            "user": {
                "id": db_token.user.id,
                "email": db_token.user.email
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
