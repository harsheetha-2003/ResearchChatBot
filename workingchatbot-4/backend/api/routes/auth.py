# api/routes/auth.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.schema import SessionLocal, User
from datetime import datetime

router = APIRouter()

class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    created_at: datetime

@router.post("/register")
async def register_user(request: RegisterRequest):
    """Register a new user"""
    try:
        db = SessionLocal()
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            db.close()
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        new_user = User(
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            password=request.password  # Note: In production, hash the password
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        db.close()
        
        return {
            "message": "User registered successfully",
            "user": {
                "id": new_user.id,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "email": new_user.email,
                "created_at": new_user.created_at
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during registration")

@router.post("/login")
async def login_user(request: LoginRequest):
    """Login user with email and password"""
    try:
        db = SessionLocal()
        
        # Find user by email
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            db.close()
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Check password (in production, compare hashed passwords)
        if user.password != request.password:
            db.close()
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        db.close()
        
        return {
            "message": "Login successful",
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "created_at": user.created_at
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during login")

@router.get("/users")
async def view_users():
    """View all registered users"""
    try:
        db = SessionLocal()
        users = db.query(User).all()
        db.close()
        
        return {
            "message": "Users retrieved successfully",
            "users": [
                {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "created_at": user.created_at
                }
                for user in users
            ]
        }
        
    except Exception as e:
        print(f"View users error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving users")