import json
from pathlib import Path
from typing import Dict, List, Set

from scraper.helpers import read_json, write_json

HISTORY_FILE = Path("data/downloads.json")
SHARING_FILE = Path("data/sharing.json")

class HistoryManager:
    """Manages the history of downloaded lessons to prevent redundant downloads."""
    
    def __init__(self):
        self._ensure_file()
        self.data = read_json(HISTORY_FILE) or {"courses": {}}

    def _ensure_file(self):
        if not HISTORY_FILE.exists():
            write_json(HISTORY_FILE, {"courses": {}})

    def is_downloaded(self, course_slug: str, lesson_slug: str) -> bool:
        """Check if a specific lesson has been successfully downloaded."""
        course_data = self.data.get("courses", {}).get(course_slug, {})
        return lesson_slug in course_data.get("completed_lessons", [])

    def mark_completed(self, course_slug: str, lesson_slug: str, title: str, 
                        course_title: str = "", path: str = "", metadata: Dict = None, 
                        lesson_metadata: Dict = None):
        """Mark a lesson as successfully downloaded with optional course metadata."""
        if "courses" not in self.data:
            self.data["courses"] = {}
            
        if course_slug not in self.data["courses"]:
            self.data["courses"][course_slug] = {
                "title": course_title or course_slug,
                "path": path,
                "completed_lessons": [],
                "thumbnail_url": metadata.get("thumbnail_url") if metadata else None,
                "logo_url": metadata.get("logo_url") if metadata else None,
                "category": metadata.get("category") if metadata else None,
                "author": metadata.get("author") if metadata else None,
                "total_duration": metadata.get("total_duration") if metadata else None,
                "total_lessons": metadata.get("total_lessons") if metadata else 0
            }
        
        # Update path and metadata if provided and not set
        if path and not self.data["courses"][course_slug].get("path"):
            self.data["courses"][course_slug]["path"] = path
        
        if metadata:
            for key in ["thumbnail_url", "logo_url", "category", "author", "total_duration", "total_lessons"]:
                if key in metadata and metadata[key] is not None:
                    # Overwrite if missing or if it's a count/duration that might have been null
                    if not self.data["courses"][course_slug].get(key) or key in ["total_duration", "total_lessons"]:
                         self.data["courses"][course_slug][key] = metadata[key]

        # Update lesson metadata
        if lesson_metadata:
            if "lessons_metadata" not in self.data["courses"][course_slug]:
                self.data["courses"][course_slug]["lessons_metadata"] = {}
            self.data["courses"][course_slug]["lessons_metadata"][lesson_slug] = lesson_metadata
        
        # New: Detailed History tracking for existence verification
        if "history" not in self.data["courses"][course_slug]:
            self.data["courses"][course_slug]["history"] = {}
        
        # Store lesson entry with path for verification
        self.data["courses"][course_slug]["history"][lesson_slug] = {
            "title": title,
            "local_path": lesson_metadata.get("local_path") if lesson_metadata else None,
            "completed_at": self.data["courses"][course_slug]["history"].get(lesson_slug, {}).get("completed_at") or None
        }

        if lesson_slug not in self.data["courses"][course_slug]["completed_lessons"]:
            from datetime import datetime
            self.data["courses"][course_slug]["completed_lessons"].append(lesson_slug)
            self.data["courses"][course_slug]["history"][lesson_slug]["completed_at"] = datetime.utcnow().isoformat()
            write_json(HISTORY_FILE, self.data)

        if lesson_slug not in self.data["courses"][course_slug]["completed_lessons"]:
            self.data["courses"][course_slug]["completed_lessons"].append(lesson_slug)
            write_json(HISTORY_FILE, self.data)

    def check_integrity(self) -> Dict:
        """Verify if the registered course paths still exist on disk."""
        results = {}
        for slug, info in self.data.get("courses", {}).items():
            path = info.get("path")
            exists = Path(path).exists() if path else False
            results[slug] = exists
        return results

    def update_gdrive_info(
        self,
        course_slug: str,
        folder_id: str,
        folder_url: str,
        shared: bool = False,
    ) -> None:
        """Persist Google Drive sync metadata for a course."""
        from datetime import datetime

        if course_slug not in self.data.get("courses", {}):
            return
        self.data["courses"][course_slug].update({
            "gdrive_folder_id": folder_id,
            "gdrive_folder_url": folder_url,
            "gdrive_synced_at": datetime.utcnow().isoformat(),
            "gdrive_shared": shared,
        })
        write_json(HISTORY_FILE, self.data)

    def add_course(self, slug: str, info: Dict) -> None:
        """Add a course entry to history (used for remote-only courses)."""
        if "courses" not in self.data:
            self.data["courses"] = {}
        self.data["courses"][slug] = info
        write_json(HISTORY_FILE, self.data)

    def remove_gdrive_info(self, course_slug: str) -> None:
        """Clear Google Drive sync metadata for a course."""
        if course_slug not in self.data.get("courses", {}):
            return
        c = self.data["courses"][course_slug]
        c.pop("gdrive_folder_id", None)
        c.pop("gdrive_folder_url", None)
        c.pop("gdrive_synced_at", None)
        c.pop("gdrive_shared", None)
        write_json(HISTORY_FILE, self.data)

    def get_history(self) -> Dict:
        """Return the full download history."""
        return self.data

    def get_verified_history(self) -> Dict:
        """Return history but UNMARK lessons where files are missing from disk."""
        import os
        verified_data = json.loads(json.dumps(self.data)) # Deep copy
        
        for slug, course in verified_data.get("courses", {}).items():
            completed = []
            history_map = {}
            
            # Check each lesson in the history map
            old_history = course.get("history", {})
            for lesson_slug, info in old_history.items():
                local_path = info.get("local_path")
                if local_path:
                    # Resolve path relative to project root or use absolute
                    p = Path(local_path)
                    if p.exists():
                        completed.append(lesson_slug)
                        history_map[lesson_slug] = True
                    else:
                        history_map[lesson_slug] = False
                else:
                    # Fallback for legacy entries without path: trust the flag but mark as unverified
                    if lesson_slug in course.get("completed_lessons", []):
                        completed.append(lesson_slug)
                        history_map[lesson_slug] = True
            
            course["completed_lessons"] = completed
            course["history"] = history_map
            course["exists"] = Path(course.get("path")).exists() if course.get("path") else False
            
        return verified_data


class SharingManager:
    """Manages logs of shared courses/emails."""
    
    def __init__(self):
        self._ensure_file()
        self.data = read_json(SHARING_FILE) or {"logs": []}

    def _ensure_file(self):
        if not SHARING_FILE.exists():
            if not SHARING_FILE.parent.exists():
                SHARING_FILE.parent.mkdir(parents=True, exist_ok=True)
            write_json(SHARING_FILE, {"logs": []})

    def add_log(self, course_slug: str, course_title: str, email: str, folder_url: str):
        """Add a new sharing record."""
        from datetime import datetime
        now = datetime.utcnow()
        log_id = f"{course_slug}_{email}_{int(now.timestamp())}"
        new_log = {
            "id": log_id,
            "slug": course_slug,
            "title": course_title,
            "email": email,
            "url": folder_url,
            "timestamp": now.isoformat()
        }
        self.data["logs"].append(new_log)
        write_json(SHARING_FILE, self.data)
        return new_log

    def get_logs(self) -> List[Dict]:
        """Return all sharing logs."""
        return self.data["logs"]

    def delete_log(self, log_id: str):
        """Delete a sharing record by ID."""
        self.data["logs"] = [l for l in self.data["logs"] if l["id"] != log_id]
        write_json(SHARING_FILE, self.data)

    def update_log(self, log_id: str, email: str):
        """Update email in a record."""
        for l in self.data["logs"]:
            if l["id"] == log_id:
                l["email"] = email
                break
        write_json(SHARING_FILE, self.data)


class LogManager:
    """Manages system activity events (downloads, errors, syncs)."""
    
    def __init__(self):
        self.file = Path("data/events.json")
        self._ensure_file()
        raw_data = read_json(self.file)
        if isinstance(raw_data, list):
            self.data = {"events": raw_data}
        else:
            self.data = raw_data or {"events": []}

    def _ensure_file(self):
        if not self.file.exists():
            write_json(self.file, {"events": []})

    def add_event(self, type: str, message: str, slug: str = None, status: str = "info"):
        from datetime import datetime
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": type,
            "message": message,
            "slug": slug,
            "status": status # info, success, warning, error
        }
        self.data["events"].append(event)
        # Keep last 500 events
        if len(self.data["events"]) > 500:
            self.data["events"] = self.data["events"][-500:]
        write_json(self.file, self.data)
        return event

    def get_events(self, limit: int = 100) -> List[Dict]:
        return self.data["events"][-limit:][::-1] # Reverse cron


history_manager = HistoryManager()
sharing_manager = SharingManager()
log_manager = LogManager()
