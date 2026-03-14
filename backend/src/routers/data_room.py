import os
import secrets
import shutil
from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File, Form, Response, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, timezone
from src.database import get_db
from src.models.user import User
from src.models.data_room import DataRoomFolder, DataRoomFile, DataRoomShareLink, DataRoomAccessLog
from src.schemas.data_room import (
    FolderCreate,
    FolderUpdate,
    FolderOut,
    FileUpdate,
    FileOut,
    ShareLinkCreate,
    ShareLinkUpdate,
    ShareLinkOut,
    AccessLogOut,
    RetentionAlertOut,
    RetentionSummaryOut,
    SharedFileOut,
    SharedFolderOut,
)
from src.utils.security import get_current_user

router = APIRouter(
    prefix="/companies/{company_id}/data-room",
    tags=["data-room"],
)

UPLOAD_BASE_DIR = "uploads/data_room"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _upload_dir(company_id: int) -> str:
    path = os.path.join(UPLOAD_BASE_DIR, str(company_id))
    os.makedirs(path, exist_ok=True)
    return path


def _serialize_folder(f: DataRoomFolder) -> dict:
    return {
        "id": f.id,
        "company_id": f.company_id,
        "name": f.name,
        "parent_id": f.parent_id,
        "folder_type": f.folder_type,
        "sort_order": f.sort_order,
        "created_at": f.created_at.isoformat() if f.created_at else "",
        "updated_at": f.updated_at.isoformat() if f.updated_at else "",
        "children": [],
    }


def _build_folder_tree(folders: List[DataRoomFolder]) -> List[dict]:
    """Build nested folder tree from flat list."""
    folder_map: Dict[int, dict] = {}
    roots: List[dict] = []

    for f in folders:
        folder_map[f.id] = _serialize_folder(f)

    for f in folders:
        node = folder_map[f.id]
        if f.parent_id and f.parent_id in folder_map:
            folder_map[f.parent_id]["children"].append(node)
        else:
            roots.append(node)

    return roots


def _serialize_file(f: DataRoomFile) -> dict:
    return {
        "id": f.id,
        "company_id": f.company_id,
        "folder_id": f.folder_id,
        "uploaded_by": f.uploaded_by,
        "filename": f.filename,
        "original_filename": f.original_filename,
        "file_size": f.file_size or 0,
        "mime_type": f.mime_type,
        "description": f.description,
        "tags": f.tags or [],
        "retention_category": f.retention_category,
        "retention_until": f.retention_until.isoformat() if f.retention_until else None,
        "version": f.version or 1,
        "previous_version_id": f.previous_version_id,
        "is_archived": f.is_archived or False,
        "created_at": f.created_at.isoformat() if f.created_at else "",
        "updated_at": f.updated_at.isoformat() if f.updated_at else "",
    }


def _serialize_share_link(sl: DataRoomShareLink) -> dict:
    return {
        "id": sl.id,
        "company_id": sl.company_id,
        "created_by": sl.created_by,
        "share_token": sl.share_token,
        "name": sl.name,
        "folder_ids": sl.folder_ids or [],
        "file_ids": sl.file_ids or [],
        "expires_at": sl.expires_at.isoformat() if sl.expires_at else None,
        "max_downloads": sl.max_downloads,
        "download_count": sl.download_count or 0,
        "last_accessed": sl.last_accessed.isoformat() if sl.last_accessed else None,
        "is_active": sl.is_active if sl.is_active is not None else True,
        "created_at": sl.created_at.isoformat() if sl.created_at else "",
        "updated_at": sl.updated_at.isoformat() if sl.updated_at else "",
    }


def _serialize_access_log(log: DataRoomAccessLog) -> dict:
    return {
        "id": log.id,
        "share_link_id": log.share_link_id,
        "file_id": log.file_id,
        "company_id": log.company_id,
        "action": log.action,
        "ip_address": log.ip_address,
        "user_agent": log.user_agent,
        "accessed_at": log.accessed_at.isoformat() if log.accessed_at else "",
    }


# ---------------------------------------------------------------------------
# Default folder structure
# ---------------------------------------------------------------------------

DEFAULT_FOLDERS = [
    {"name": "Incorporation Documents", "folder_type": "INCORPORATION", "sort_order": 1, "retention": "PERMANENT"},
    {"name": "Board Meetings & Resolutions", "folder_type": "BOARD_MEETINGS", "sort_order": 2, "retention": "PERMANENT"},
    {"name": "Shareholder Meetings (AGM/EGM)", "folder_type": "BOARD_MEETINGS", "sort_order": 3, "retention": "PERMANENT"},
    {"name": "Compliance & Filings", "folder_type": "COMPLIANCE", "sort_order": 4, "retention": "8_YEARS"},
    {"name": "Financial Statements & Audit Reports", "folder_type": "FINANCIALS", "sort_order": 5, "retention": "8_YEARS"},
    {"name": "Agreements & Contracts", "folder_type": "AGREEMENTS", "sort_order": 6, "retention": "8_YEARS"},
    {"name": "Cap Table & Share Certificates", "folder_type": "CAP_TABLE", "sort_order": 7, "retention": "PERMANENT"},
    {"name": "IP & Trademarks", "folder_type": "IP", "sort_order": 8, "retention": "PERMANENT"},
    {"name": "HR & Employment Records", "folder_type": "HR", "sort_order": 9, "retention": "6_YEARS"},
    {"name": "Tax Records", "folder_type": "TAX", "sort_order": 10, "retention": "6_YEARS"},
]


# ---------------------------------------------------------------------------
# Folder endpoints
# ---------------------------------------------------------------------------


@router.get("/folders")
def list_folders(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all folders (tree structure)."""
    folders = (
        db.query(DataRoomFolder)
        .filter(DataRoomFolder.company_id == company_id)
        .order_by(DataRoomFolder.sort_order.asc(), DataRoomFolder.name.asc())
        .all()
    )
    return _build_folder_tree(folders)


@router.post("/folders", status_code=status.HTTP_201_CREATED)
def create_folder(
    company_id: int,
    body: FolderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new folder."""
    if body.parent_id:
        parent = (
            db.query(DataRoomFolder)
            .filter(
                DataRoomFolder.id == body.parent_id,
                DataRoomFolder.company_id == company_id,
            )
            .first()
        )
        if not parent:
            raise HTTPException(status_code=404, detail="Parent folder not found")

    folder = DataRoomFolder(
        company_id=company_id,
        name=body.name,
        parent_id=body.parent_id,
        folder_type=body.folder_type,
        sort_order=body.sort_order,
    )
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return _serialize_folder(folder)


@router.put("/folders/{folder_id}")
def update_folder(
    company_id: int,
    folder_id: int,
    body: FolderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Rename/move folder."""
    folder = (
        db.query(DataRoomFolder)
        .filter(DataRoomFolder.id == folder_id, DataRoomFolder.company_id == company_id)
        .first()
    )
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    if body.name is not None:
        folder.name = body.name
    if body.parent_id is not None:
        # Prevent moving folder into itself
        if body.parent_id == folder_id:
            raise HTTPException(status_code=400, detail="Cannot move folder into itself")
        folder.parent_id = body.parent_id
    if body.sort_order is not None:
        folder.sort_order = body.sort_order

    db.commit()
    db.refresh(folder)
    return _serialize_folder(folder)


@router.delete("/folders/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_folder(
    company_id: int,
    folder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete empty folder."""
    folder = (
        db.query(DataRoomFolder)
        .filter(DataRoomFolder.id == folder_id, DataRoomFolder.company_id == company_id)
        .first()
    )
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # Check for files
    file_count = (
        db.query(DataRoomFile)
        .filter(DataRoomFile.folder_id == folder_id, DataRoomFile.is_archived == False)
        .count()
    )
    if file_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete folder with files. Remove or archive files first.")

    # Check for child folders
    child_count = (
        db.query(DataRoomFolder)
        .filter(DataRoomFolder.parent_id == folder_id)
        .count()
    )
    if child_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete folder with sub-folders.")

    db.delete(folder)
    db.commit()
    return None


# ---------------------------------------------------------------------------
# File endpoints
# ---------------------------------------------------------------------------


@router.post("/folders/{folder_id}/files", status_code=status.HTTP_201_CREATED)
def upload_file(
    company_id: int,
    folder_id: int,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # Comma-separated
    retention_category: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload file to a folder."""
    folder = (
        db.query(DataRoomFolder)
        .filter(DataRoomFolder.id == folder_id, DataRoomFolder.company_id == company_id)
        .first()
    )
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # Save file to disk
    upload_dir = _upload_dir(company_id)
    unique_name = f"{secrets.token_hex(8)}_{file.filename}"
    file_path = os.path.join(upload_dir, unique_name)

    with open(file_path, "wb") as f:
        content = file.file.read()
        f.write(content)
        file_size = len(content)

    tags_list = [t.strip() for t in tags.split(",")] if tags else []

    db_file = DataRoomFile(
        company_id=company_id,
        folder_id=folder_id,
        uploaded_by=current_user.id,
        filename=unique_name,
        original_filename=file.filename or "unnamed",
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type,
        description=description,
        tags=tags_list,
        retention_category=retention_category,
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return _serialize_file(db_file)


@router.get("/files")
def list_files(
    company_id: int,
    folder_id: Optional[int] = Query(None),
    tag: Optional[str] = Query(None),
    retention_category: Optional[str] = Query(None),
    include_archived: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all files (optional filter by folder, tags, retention)."""
    query = db.query(DataRoomFile).filter(DataRoomFile.company_id == company_id)

    if not include_archived:
        query = query.filter(DataRoomFile.is_archived == False)
    if folder_id is not None:
        query = query.filter(DataRoomFile.folder_id == folder_id)
    if retention_category:
        query = query.filter(DataRoomFile.retention_category == retention_category)

    files = query.order_by(DataRoomFile.created_at.desc()).all()

    # Filter by tag in Python (JSON column)
    if tag:
        files = [f for f in files if tag in (f.tags or [])]

    return [_serialize_file(f) for f in files]


@router.get("/files/{file_id}")
def get_file_metadata(
    company_id: int,
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get file metadata."""
    db_file = (
        db.query(DataRoomFile)
        .filter(DataRoomFile.id == file_id, DataRoomFile.company_id == company_id)
        .first()
    )
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    return _serialize_file(db_file)


@router.get("/files/{file_id}/download")
def download_file(
    company_id: int,
    file_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download file."""
    db_file = (
        db.query(DataRoomFile)
        .filter(DataRoomFile.id == file_id, DataRoomFile.company_id == company_id)
        .first()
    )
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    if not os.path.exists(db_file.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    # Log access
    log = DataRoomAccessLog(
        file_id=file_id,
        company_id=company_id,
        action="download",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(log)
    db.commit()

    return FileResponse(
        path=db_file.file_path,
        filename=db_file.original_filename,
        media_type=db_file.mime_type or "application/octet-stream",
    )


@router.put("/files/{file_id}")
def update_file_metadata(
    company_id: int,
    file_id: int,
    body: FileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update file metadata (description, tags, retention)."""
    db_file = (
        db.query(DataRoomFile)
        .filter(DataRoomFile.id == file_id, DataRoomFile.company_id == company_id)
        .first()
    )
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    if body.description is not None:
        db_file.description = body.description
    if body.tags is not None:
        db_file.tags = body.tags
    if body.retention_category is not None:
        db_file.retention_category = body.retention_category
    if body.retention_until is not None:
        try:
            db_file.retention_until = datetime.fromisoformat(body.retention_until)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid retention_until date format.")

    db.commit()
    db.refresh(db_file)
    return _serialize_file(db_file)


@router.delete("/files/{file_id}")
def archive_file(
    company_id: int,
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft delete (archive) file."""
    db_file = (
        db.query(DataRoomFile)
        .filter(DataRoomFile.id == file_id, DataRoomFile.company_id == company_id)
        .first()
    )
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    db_file.is_archived = True
    db.commit()
    db.refresh(db_file)
    return {"message": "File archived", "file_id": file_id}


@router.post("/files/{file_id}/new-version", status_code=status.HTTP_201_CREATED)
def upload_new_version(
    company_id: int,
    file_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload new version of a file."""
    existing = (
        db.query(DataRoomFile)
        .filter(DataRoomFile.id == file_id, DataRoomFile.company_id == company_id)
        .first()
    )
    if not existing:
        raise HTTPException(status_code=404, detail="File not found")

    # Save new file
    upload_dir = _upload_dir(company_id)
    unique_name = f"{secrets.token_hex(8)}_{file.filename}"
    file_path = os.path.join(upload_dir, unique_name)

    with open(file_path, "wb") as f:
        content = file.file.read()
        f.write(content)
        file_size = len(content)

    new_file = DataRoomFile(
        company_id=company_id,
        folder_id=existing.folder_id,
        uploaded_by=current_user.id,
        filename=unique_name,
        original_filename=file.filename or existing.original_filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=file.content_type,
        description=existing.description,
        tags=existing.tags,
        retention_category=existing.retention_category,
        retention_until=existing.retention_until,
        version=(existing.version or 1) + 1,
        previous_version_id=existing.id,
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return _serialize_file(new_file)


# ---------------------------------------------------------------------------
# Share link endpoints
# ---------------------------------------------------------------------------


@router.post("/share-links", status_code=status.HTTP_201_CREATED)
def create_share_link(
    company_id: int,
    body: ShareLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create share link."""
    expires_at = None
    if body.expires_at:
        try:
            expires_at = datetime.fromisoformat(body.expires_at)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid expires_at date format.")

    password_hash = None
    if body.password:
        from src.utils.security import get_password_hash
        password_hash = get_password_hash(body.password)

    share_link = DataRoomShareLink(
        company_id=company_id,
        created_by=current_user.id,
        share_token=secrets.token_urlsafe(32),
        name=body.name,
        folder_ids=body.folder_ids,
        file_ids=body.file_ids,
        password_hash=password_hash,
        expires_at=expires_at,
        max_downloads=body.max_downloads,
    )
    db.add(share_link)
    db.commit()
    db.refresh(share_link)
    return _serialize_share_link(share_link)


@router.get("/share-links")
def list_share_links(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List active share links."""
    links = (
        db.query(DataRoomShareLink)
        .filter(
            DataRoomShareLink.company_id == company_id,
            DataRoomShareLink.is_active == True,
        )
        .order_by(DataRoomShareLink.created_at.desc())
        .all()
    )
    return [_serialize_share_link(sl) for sl in links]


@router.put("/share-links/{link_id}")
def update_share_link(
    company_id: int,
    link_id: int,
    body: ShareLinkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update share link (toggle active, update expiry)."""
    link = (
        db.query(DataRoomShareLink)
        .filter(DataRoomShareLink.id == link_id, DataRoomShareLink.company_id == company_id)
        .first()
    )
    if not link:
        raise HTTPException(status_code=404, detail="Share link not found")

    if body.is_active is not None:
        link.is_active = body.is_active
    if body.expires_at is not None:
        try:
            link.expires_at = datetime.fromisoformat(body.expires_at)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid expires_at date format.")
    if body.max_downloads is not None:
        link.max_downloads = body.max_downloads

    db.commit()
    db.refresh(link)
    return _serialize_share_link(link)


@router.delete("/share-links/{link_id}")
def deactivate_share_link(
    company_id: int,
    link_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deactivate share link."""
    link = (
        db.query(DataRoomShareLink)
        .filter(DataRoomShareLink.id == link_id, DataRoomShareLink.company_id == company_id)
        .first()
    )
    if not link:
        raise HTTPException(status_code=404, detail="Share link not found")

    link.is_active = False
    db.commit()
    return {"message": "Share link deactivated", "link_id": link_id}


@router.get("/share-links/{link_id}/access-log")
def get_access_log(
    company_id: int,
    link_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """View access log for a share link."""
    link = (
        db.query(DataRoomShareLink)
        .filter(DataRoomShareLink.id == link_id, DataRoomShareLink.company_id == company_id)
        .first()
    )
    if not link:
        raise HTTPException(status_code=404, detail="Share link not found")

    logs = (
        db.query(DataRoomAccessLog)
        .filter(DataRoomAccessLog.share_link_id == link_id)
        .order_by(DataRoomAccessLog.accessed_at.desc())
        .all()
    )
    return [_serialize_access_log(log) for log in logs]


# ---------------------------------------------------------------------------
# Retention endpoints
# ---------------------------------------------------------------------------


@router.get("/retention/alerts")
def retention_alerts(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Files approaching retention expiry (within 90 days)."""
    now = datetime.now(timezone.utc)
    threshold = now + timedelta(days=90)

    files = (
        db.query(DataRoomFile)
        .filter(
            DataRoomFile.company_id == company_id,
            DataRoomFile.is_archived == False,
            DataRoomFile.retention_until != None,
            DataRoomFile.retention_until <= threshold,
        )
        .order_by(DataRoomFile.retention_until.asc())
        .all()
    )

    results = []
    for f in files:
        days_remaining = (f.retention_until - now).days if f.retention_until else 0
        results.append({
            "file_id": f.id,
            "filename": f.filename,
            "original_filename": f.original_filename,
            "retention_category": f.retention_category,
            "retention_until": f.retention_until.isoformat() if f.retention_until else None,
            "folder_id": f.folder_id,
            "days_remaining": days_remaining,
        })

    return results


@router.get("/retention/summary")
def retention_summary(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retention compliance summary."""
    now = datetime.now(timezone.utc)
    threshold = now + timedelta(days=90)

    files = (
        db.query(DataRoomFile)
        .filter(DataRoomFile.company_id == company_id, DataRoomFile.is_archived == False)
        .all()
    )

    total = len(files)
    permanent = sum(1 for f in files if f.retention_category == "PERMANENT")
    eight_years = sum(1 for f in files if f.retention_category == "8_YEARS")
    six_years = sum(1 for f in files if f.retention_category == "6_YEARS")
    three_years = sum(1 for f in files if f.retention_category == "3_YEARS")
    custom = sum(1 for f in files if f.retention_category == "CUSTOM")
    no_retention = sum(1 for f in files if not f.retention_category)
    expiring_soon = sum(
        1 for f in files
        if f.retention_until and f.retention_until <= threshold
    )

    return {
        "total_files": total,
        "permanent": permanent,
        "eight_years": eight_years,
        "six_years": six_years,
        "three_years": three_years,
        "custom": custom,
        "no_retention": no_retention,
        "expiring_soon": expiring_soon,
    }


# ---------------------------------------------------------------------------
# Setup defaults
# ---------------------------------------------------------------------------


@router.post("/setup-defaults", status_code=status.HTTP_201_CREATED)
def setup_default_folders(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create default folder structure for company."""
    existing = (
        db.query(DataRoomFolder)
        .filter(DataRoomFolder.company_id == company_id)
        .count()
    )
    if existing > 0:
        raise HTTPException(
            status_code=400,
            detail="Default folders already exist for this company. Delete existing folders first or create folders manually.",
        )

    created_folders = []
    for folder_def in DEFAULT_FOLDERS:
        folder = DataRoomFolder(
            company_id=company_id,
            name=folder_def["name"],
            folder_type=folder_def["folder_type"],
            sort_order=folder_def["sort_order"],
        )
        db.add(folder)
        created_folders.append(folder)

    db.commit()
    for f in created_folders:
        db.refresh(f)

    # Create upload directory
    _upload_dir(company_id)

    return [_serialize_folder(f) for f in created_folders]


# ---------------------------------------------------------------------------
# Public share link access (no auth required)
# ---------------------------------------------------------------------------


@router.get("/shared/{share_token}")
def access_shared_data_room(
    company_id: int,
    share_token: str,
    request: Request,
    password: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Access shared data room (list files/folders in share). No auth required."""
    link = (
        db.query(DataRoomShareLink)
        .filter(
            DataRoomShareLink.share_token == share_token,
            DataRoomShareLink.company_id == company_id,
            DataRoomShareLink.is_active == True,
        )
        .first()
    )
    if not link:
        raise HTTPException(status_code=404, detail="Share link not found or inactive")

    # Check expiry
    if link.expires_at and datetime.now(timezone.utc) > link.expires_at:
        raise HTTPException(status_code=410, detail="Share link has expired")

    # Check password
    if link.password_hash:
        if not password:
            raise HTTPException(status_code=401, detail="Password required")
        from src.utils.security import verify_password
        if not verify_password(password, link.password_hash):
            raise HTTPException(status_code=401, detail="Invalid password")

    # Log access
    log = DataRoomAccessLog(
        share_link_id=link.id,
        company_id=company_id,
        action="share_link_access",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(log)
    link.last_accessed = datetime.now(timezone.utc)
    db.commit()

    # Gather shared folders
    shared_folders = []
    folder_ids = link.folder_ids or []
    if folder_ids:
        folders = (
            db.query(DataRoomFolder)
            .filter(
                DataRoomFolder.id.in_(folder_ids),
                DataRoomFolder.company_id == company_id,
            )
            .all()
        )
        for folder in folders:
            files = (
                db.query(DataRoomFile)
                .filter(
                    DataRoomFile.folder_id == folder.id,
                    DataRoomFile.company_id == company_id,
                    DataRoomFile.is_archived == False,
                )
                .all()
            )
            shared_folders.append({
                "id": folder.id,
                "name": folder.name,
                "files": [
                    {
                        "id": f.id,
                        "filename": f.filename,
                        "original_filename": f.original_filename,
                        "file_size": f.file_size or 0,
                        "mime_type": f.mime_type,
                        "description": f.description,
                    }
                    for f in files
                ],
            })

    # Gather individually shared files
    shared_files = []
    file_ids = link.file_ids or []
    if file_ids:
        files = (
            db.query(DataRoomFile)
            .filter(
                DataRoomFile.id.in_(file_ids),
                DataRoomFile.company_id == company_id,
                DataRoomFile.is_archived == False,
            )
            .all()
        )
        shared_files = [
            {
                "id": f.id,
                "filename": f.filename,
                "original_filename": f.original_filename,
                "file_size": f.file_size or 0,
                "mime_type": f.mime_type,
                "description": f.description,
            }
            for f in files
        ]

    return {
        "name": link.name,
        "folders": shared_folders,
        "files": shared_files,
    }


@router.get("/shared/{share_token}/files/{file_id}")
def download_shared_file(
    company_id: int,
    share_token: str,
    file_id: int,
    request: Request,
    password: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Download file via share link. No auth required."""
    link = (
        db.query(DataRoomShareLink)
        .filter(
            DataRoomShareLink.share_token == share_token,
            DataRoomShareLink.company_id == company_id,
            DataRoomShareLink.is_active == True,
        )
        .first()
    )
    if not link:
        raise HTTPException(status_code=404, detail="Share link not found or inactive")

    # Check expiry
    if link.expires_at and datetime.now(timezone.utc) > link.expires_at:
        raise HTTPException(status_code=410, detail="Share link has expired")

    # Check password
    if link.password_hash:
        if not password:
            raise HTTPException(status_code=401, detail="Password required")
        from src.utils.security import verify_password
        if not verify_password(password, link.password_hash):
            raise HTTPException(status_code=401, detail="Invalid password")

    # Check max downloads
    if link.max_downloads and (link.download_count or 0) >= link.max_downloads:
        raise HTTPException(status_code=410, detail="Download limit reached")

    # Check file is part of the share
    db_file = (
        db.query(DataRoomFile)
        .filter(DataRoomFile.id == file_id, DataRoomFile.company_id == company_id)
        .first()
    )
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")

    # Verify file is in shared scope
    file_ids = link.file_ids or []
    folder_ids = link.folder_ids or []
    if file_id not in file_ids and db_file.folder_id not in folder_ids:
        raise HTTPException(status_code=403, detail="File not included in this share link")

    if not os.path.exists(db_file.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    # Log access and increment download count
    log = DataRoomAccessLog(
        share_link_id=link.id,
        file_id=file_id,
        company_id=company_id,
        action="download",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(log)
    link.download_count = (link.download_count or 0) + 1
    link.last_accessed = datetime.now(timezone.utc)
    db.commit()

    return FileResponse(
        path=db_file.file_path,
        filename=db_file.original_filename,
        media_type=db_file.mime_type or "application/octet-stream",
    )
