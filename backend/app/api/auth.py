from typing import Dict
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from scraper.api import AsyncPlatzi
from scraper.constants import SESSION_FILE
from backend.app.api.logs import add_event
from backend.app.core.history import log_manager

router = APIRouter(prefix="/api", tags=["auth"])

@router.get("/me")
async def get_me():
    try:
        async with AsyncPlatzi(headless=True) as platzi:
            if platzi.loggedin and platzi.user:
                add_event("auth", "Verificación de sesión activa", "INFO", {"email": platzi.user.email})
                return {
                    "logged_in": True, 
                    "email": platzi.user.email or platzi.user.username, 
                    "name": platzi.user.name
                }
            return {"logged_in": False}
    except Exception:
        return {"logged_in": False}

@router.post("/login")
async def login(data: Dict):
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return JSONResponse({"status": "error", "message": "Email and password required"}, status_code=400)
    
    try:
        # Lanza el modo headed (ventana visible) para poder resolver captchas o llenar manual
        async with AsyncPlatzi(headless=False) as platzi:
            await platzi.login(email=email, password=password)
            log_manager.add_event("auth", f"Login exitoso: {email}", status="success")
            # Log success
            add_event("auth", f"Sesión iniciada: {email}", "INFO", {"email": email})
            return {"status": "success", "message": "Login successful"}
    except Exception as e:
        add_event("auth", f"Fallo de login: {email}", "WARNING", {"email": email, "error": str(e)})
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@router.post("/logout")
async def logout_platzi():
    try:
        async with AsyncPlatzi(headless=True) as platzi:
            await platzi.logout()
            log_manager.add_event("auth", "Sesión cerrada", status="info")
            if SESSION_FILE.exists():
                os.remove(SESSION_FILE)
            add_event("auth", "Sesión cerrada correctamente", "INFO")
        return {"status": "success"}
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
