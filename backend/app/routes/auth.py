from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
import logging

from ..config.database import get_db
from ..config.settings import settings
from ..models.user import User
from ..schemas.user import UserCreate, UserResponse
from ..utils.validators import validate_email, validate_password

router = APIRouter()
logger = logging.getLogger(__name__)

# Security setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Ensure bytes for bcrypt
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
        
    # Truncate plain password to 70 bytes to match hash generation
    if len(plain_password) > 70:
        plain_password = plain_password[:70]
        
    return bcrypt.checkpw(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    # Truncate to 70 bytes to be safe
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 70:
        password_bytes = password_bytes[:70]
    
    # Debug logging
    logger.info(f"Hashing password: {len(password)} chars, {len(password_bytes)} bytes")
    
    # Hash using bcrypt directly
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')

def authenticate_user(db: Session, username_or_email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(
        (User.email == username_or_email) | (User.username == username_or_email)
    ).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Validate email
    validate_email(user_data.email)
    
    # Validate password
    logger.info(f"Registering user: {user_data.email}")
    logger.info(f"Password length: {len(user_data.password)}")
    validate_password(user_data.password)
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username
    }

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user