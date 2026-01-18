from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
from datetime import datetime, timedelta

app = FastAPI(title="Authentication Service")

# --- Security & Utils ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db = {}  # In-memory user store: username -> hashed_password

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# --- Models ---
class UserAuth(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    message: Optional[str] = None

# --- Endpoints ---
@app.post("/signup", response_model=UserResponse)
async def signup(user: UserAuth):
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=400, 
            detail="Username already registered"
        )
    fake_users_db[user.username] = get_password_hash(user.password)
    return UserResponse(username=user.username, message="User created successfully")

@app.post("/login")
async def login(user: UserAuth):
    hashed_password = fake_users_db.get(user.username)
    if not hashed_password or not verify_password(user.password, hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # For simplicity in this exam, we return the username as a 'token' 
    # In a real app, this would be a JWT
    return {"access_token": user.username, "token_type": "bearer"}

@app.get("/me")
async def me(token: str):
    # Determine user from token (username in this simple case)
    if token not in fake_users_db:
         raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"username": token}
