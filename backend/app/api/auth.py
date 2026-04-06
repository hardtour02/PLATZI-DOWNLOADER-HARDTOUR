import os
from pathlib import Path
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from scraper.api import AsyncPlatzi
from scraper.constants import SESSION_FILE
from scraper.logger import Logger

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

@router.get("/status")
async def get_auth_status():
    """Check if we have an active session."""
    is_authenticated = SESSION_FILE.exists()
    return {"authenticated": is_authenticated}

@router.post("/login")
async def login(data: LoginRequest):
    """Attempt login and save session."""
    try:
        async with AsyncPlatzi(headless=True) as platzi:
            success = await platzi.login(data.email, data.password)
            if success:
                return {"status": "success", "message": "Logged in successfully"}
            else:
                raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        Logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout")
async def logout():
    """Remove session file."""
    if SESSION_FILE.exists():
        os.remove(SESSION_FILE)
    return {"status": "success"}
