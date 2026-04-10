import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter

router = APIRouter(prefix="/api/log", tags=["logs"])

LOG_FILE = Path("data/events.json")

def add_event(type: str, message: str, level: str = "INFO", metadata: Optional[Dict] = None):
    """Utility to register a system event."""
    if not LOG_FILE.parent.exists():
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    events = []
    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    events = data
                elif isinstance(data, dict):
                    events = data.get("events", [])
        except:
            events = []

    event = {
        "timestamp": datetime.now().isoformat(),
        "type": type, # "auth", "download", "sync", "error"
        "level": level,
        "message": message,
        "metadata": metadata or {}
    }
    
    events.insert(0, event) # Newest first
    # Keep last 100 events
    events = events[:100]
    
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

@router.get("/events")
async def get_events(limit: int = 50):
    if not LOG_FILE.exists():
        return {"events": []}
    
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            events = json.load(f)
            return {"events": events[:limit]}
    except:
        return {"events": []}
