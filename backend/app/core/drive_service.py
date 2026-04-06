"""
Google Drive synchronization manager.

Handles OAuth2 authentication, file/folder CRUD, resumable uploads
with exponential backoff, and full course‑folder mirroring.
"""

import json
import os
import time
import logging
from pathlib import Path
from typing import Callable, Dict, List, Optional

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# ── Paths & Constants ────────────────────────────────────────────────────────
CREDENTIALS_FILE = Path("data/gdrive_credentials.json")
TOKEN_FILE = Path("data/gdrive_token.json")
SCOPES = ["https://www.googleapis.com/auth/drive"]
PORT = os.getenv("PORT", "8000")
REDIRECT_URI = f"http://localhost:{PORT}/api/gdrive/auth-callback"

# Files/dirs to skip when uploading a course folder
_IGNORE_EXTENSIONS = {".pyc", ".py", ".json", ".txt", ".log"}
_IGNORE_DIRS = {"__pycache__", ".tmp"}

CHUNK_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_RETRIES = 5


class GDriveManager:
    """Encapsulates every interaction with Google Drive."""

    def __init__(self):
        self._flow: Optional[Flow] = None

    # ── Authentication ───────────────────────────────────────────────────

    def is_authenticated(self) -> bool:
        """Return *True* when a valid (or refreshable) token exists."""
        if not TOKEN_FILE.exists():
            return False
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
            if creds.valid:
                return True
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                TOKEN_FILE.write_text(creds.to_json())
                return True
        except Exception:
            pass
        return False

    def get_account_email(self) -> Optional[str]:
        """Fetch the email of the currently authenticated Google user."""
        try:
            service = self._get_service()
            about = service.about().get(fields="user").execute()
            return about.get("user", {}).get("emailAddress")
        except Exception:
            return None

    def get_auth_url(self) -> Optional[str]:
        """Build an OAuth2 authorization URL. Returns *None* if credentials.json missing."""
        if not CREDENTIALS_FILE.exists():
            return None
        self._flow = Flow.from_client_secrets_file(
            str(CREDENTIALS_FILE),
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI,
        )
        auth_url, _ = self._flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        return auth_url

    def exchange_code(self, code: str) -> bool:
        """Exchange an authorization *code* for credentials and persist them."""
        if self._flow is None:
            # Rebuild flow in case the server was restarted between requests
            if not CREDENTIALS_FILE.exists():
                return False
            self._flow = Flow.from_client_secrets_file(
                str(CREDENTIALS_FILE),
                scopes=SCOPES,
                redirect_uri=REDIRECT_URI,
            )
        try:
            self._flow.fetch_token(code=code)
            creds = self._flow.credentials
            TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
            TOKEN_FILE.write_text(creds.to_json())
            return True
        except Exception as exc:
            logger.error("exchange_code failed: %s", exc)
            return False

    def revoke(self) -> None:
        """Revoke the token in Google and delete the local file."""
        if TOKEN_FILE.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
                requests.post(
                    "https://oauth2.googleapis.com/revoke",
                    params={"token": creds.token},
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=10,
                )
            except Exception:
                pass
            TOKEN_FILE.unlink(missing_ok=True)

    def _get_service(self):
        """Return an authenticated Drive v3 service, refreshing if needed."""
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            TOKEN_FILE.write_text(creds.to_json())
        return build("drive", "v3", credentials=creds)

    # ── File operations ──────────────────────────────────────────────────

    def upload_file(self, local_path: Path, parent_folder_id: str) -> str:
        """Simple (non‑resumable) upload. Returns the new file ID."""
        service = self._get_service()
        meta = {"name": local_path.name, "parents": [parent_folder_id]}
        media = MediaFileUpload(str(local_path))
        f = service.files().create(body=meta, media_body=media, fields="id").execute()
        return f["id"]

    def upload_file_resumable(
        self,
        local_path: Path,
        parent_folder_id: str,
        progress_callback: Optional[Callable] = None,
    ) -> str:
        """Resumable upload with 10 MB chunks and exponential backoff."""
        service = self._get_service()
        meta = {"name": local_path.name, "parents": [parent_folder_id]}
        media = MediaFileUpload(
            str(local_path), resumable=True, chunksize=CHUNK_SIZE
        )
        request = service.files().create(body=meta, media_body=media, fields="id")

        response = None
        while response is None:
            for attempt in range(MAX_RETRIES):
                try:
                    status, response = request.next_chunk()
                    if status and progress_callback:
                        progress_callback(
                            status.resumable_progress, status.total_size
                        )
                    break  # success — leave retry loop
                except HttpError as err:
                    if err.resp.status in (429, 500, 503) and attempt < MAX_RETRIES - 1:
                        wait = 2**attempt
                        logger.warning("Retrying chunk (attempt %d, wait %ds)", attempt + 1, wait)
                        time.sleep(wait)
                    else:
                        raise

        return response["id"]

    def download_file(self, file_id: str, dest_path: Path) -> None:
        """Download a file by its Drive ID."""
        import io

        service = self._get_service()
        request = service.files().get_media(fileId=file_id)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

    def delete_file(self, file_id: str) -> None:
        self._get_service().files().delete(fileId=file_id).execute()

    def update_file(self, file_id: str, local_path: Path) -> None:
        service = self._get_service()
        media = MediaFileUpload(str(local_path))
        service.files().update(fileId=file_id, media_body=media).execute()

    def read_text_file(self, file_id: str) -> str:
        import io

        service = self._get_service()
        request = service.files().get_media(fileId=file_id)
        buf = io.BytesIO()
        downloader = MediaIoBaseDownload(buf, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        return buf.getvalue().decode("utf-8")

    def get_file_metadata(self, file_id: str) -> Dict:
        service = self._get_service()
        return (
            service.files()
            .get(fileId=file_id, fields="id,name,mimeType,size,modifiedTime")
            .execute()
        )

    def update_metadata(self, file_id: str, metadata: Dict) -> None:
        self._get_service().files().update(fileId=file_id, body=metadata).execute()

    # ── Folder operations ────────────────────────────────────────────────

    def create_folder(self, name: str, parent_id: Optional[str] = None) -> str:
        service = self._get_service()
        meta: Dict = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id:
            meta["parents"] = [parent_id]
        f = service.files().create(body=meta, fields="id").execute()
        return f["id"]

    def find_folder(self, name: str, parent_id: Optional[str] = None) -> Optional[str]:
        service = self._get_service()
        parent = parent_id or "root"
        q = (
            f"name = '{name}' "
            f"and mimeType = 'application/vnd.google-apps.folder' "
            f"and '{parent}' in parents "
            f"and trashed = false"
        )
        res = service.files().list(q=q, spaces="drive", fields="files(id)").execute()
        files = res.get("files", [])
        return files[0]["id"] if files else None

    def get_or_create_folder(self, name: str, parent_id: Optional[str] = None) -> str:
        fid = self.find_folder(name, parent_id)
        if fid:
            return fid
        return self.create_folder(name, parent_id)

    def list_files(self, folder_id: str) -> List[Dict]:
        service = self._get_service()
        q = f"'{folder_id}' in parents and trashed = false"
        res = (
            service.files()
            .list(q=q, spaces="drive", fields="files(id,name,mimeType)")
            .execute()
        )
        return res.get("files", [])

    def search(self, query: str) -> List[Dict]:
        service = self._get_service()
        res = (
            service.files()
            .list(q=query, spaces="drive", fields="files(id,name,mimeType,size)")
            .execute()
        )
        return res.get("files", [])

    # ── Permissions ──────────────────────────────────────────────────────

    def set_permission_public(self, file_id: str) -> None:
        service = self._get_service()
        service.permissions().create(
            fileId=file_id, body={"role": "reader", "type": "anyone"}
        ).execute()

    def set_permission_user(self, file_id: str, email: str, role: str = "reader") -> None:
        service = self._get_service()
        service.permissions().create(
            fileId=file_id,
            body={"role": role, "type": "user", "emailAddress": email},
        ).execute()

    def remove_permission(self, file_id: str, permission_id: str) -> None:
        self._get_service().permissions().delete(
            fileId=file_id, permissionId=permission_id
        ).execute()

    def list_permissions(self, file_id: str) -> List[Dict]:
        service = self._get_service()
        res = (
            service.permissions()
            .list(fileId=file_id, fields="permissions(id,role,type,emailAddress)")
            .execute()
        )
        return res.get("permissions", [])

    # ── Course‑folder upload ─────────────────────────────────────────────

    def find_file_in_folder(self, name: str, folder_id: str) -> Optional[str]:
        """Find a file by exact *name* inside *folder_id*."""
        service = self._get_service()
        q = (
            f"name = '{name}' "
            f"and '{folder_id}' in parents "
            f"and trashed = false"
        )
        res = service.files().list(q=q, spaces="drive", fields="files(id)").execute()
        files = res.get("files", [])
        return files[0]["id"] if files else None

    @staticmethod
    def _build_folder_url(folder_id: str) -> str:
        return f"https://drive.google.com/drive/folders/{folder_id}"

    @staticmethod
    def _should_ignore(path: Path) -> bool:
        """Return True for files/dirs that should NOT be uploaded."""
        name = path.name
        if name.startswith("__") or name.startswith("."):
            return True
        if path.is_file() and path.suffix.lower() in _IGNORE_EXTENSIONS:
            return True
        if path.is_dir() and name in _IGNORE_DIRS:
            return True
        return False

    def upload_course_folder(
        self,
        course_local_path: Path,
        progress_callback: Optional[Callable] = None,
    ) -> Dict:
        """
        Mirror a local course directory to Drive under ``COURSES/<course_name>``.

        Returns a dict: ``{"folder_id": str, "uploaded": int, "skipped": int, "total": int}``

        ``progress_callback(filename, uploaded_bytes, total_bytes,
                            current_file_index, total_files)``
        """
        # 1. Root container
        courses_folder_id = self.get_or_create_folder("COURSES")

        # 2. Course folder
        course_folder_id = self.get_or_create_folder(
            course_local_path.name, courses_folder_id
        )

        # 3. Collect uploadable files
        all_files: List[Path] = []
        for f in sorted(course_local_path.rglob("*")):
            if f.is_file() and not self._should_ignore(f):
                # Also skip if any ancestor dir is ignored
                skip = False
                for parent in f.relative_to(course_local_path).parents:
                    if parent.name and parent.name in _IGNORE_DIRS:
                        skip = True
                        break
                if not skip:
                    all_files.append(f)

        total_files = len(all_files)
        uploaded_count = 0
        skipped_count = 0

        # 4. Upload each file, mirroring sub‑directory structure
        for idx, fpath in enumerate(all_files):
            rel = fpath.relative_to(course_local_path)
            # Ensure parent folders exist in Drive
            parent_id = course_folder_id
            for part in rel.parts[:-1]:
                parent_id = self.get_or_create_folder(part, parent_id)

            # Skip duplicates
            existing = self.find_file_in_folder(fpath.name, parent_id)
            if existing:
                skipped_count += 1
                if progress_callback:
                    progress_callback(fpath.name, 0, 0, idx + 1, total_files)
                continue

            # Upload
            uploaded_count += 1
            if fpath.suffix.lower() == ".mp4":
                def _chunk_cb(uploaded: int, total: int, _name=fpath.name, _idx=idx):
                    if progress_callback:
                        progress_callback(_name, uploaded, total, _idx + 1, total_files)

                self.upload_file_resumable(fpath, parent_id, progress_callback=_chunk_cb)
            else:
                self.upload_file(fpath, parent_id)
                if progress_callback:
                    sz = fpath.stat().st_size
                    progress_callback(fpath.name, sz, sz, idx + 1, total_files)

        return {
            "folder_id": course_folder_id,
            "uploaded": uploaded_count,
            "skipped": skipped_count,
            "total": total_files,
        }
