from pydantic import BaseModel
from typing import Any, Dict, List, Optional


# --- Folder schemas ---

class FolderCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None
    folder_type: Optional[str] = None
    sort_order: int = 0


class FolderUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None


class FolderOut(BaseModel):
    id: int
    company_id: int
    name: str
    parent_id: Optional[int] = None
    folder_type: Optional[str] = None
    sort_order: int
    created_at: str
    updated_at: str
    children: List["FolderOut"] = []

    class Config:
        from_attributes = True


# --- File schemas ---

class FileUpdate(BaseModel):
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    retention_category: Optional[str] = None
    retention_until: Optional[str] = None


class FileOut(BaseModel):
    id: int
    company_id: int
    folder_id: int
    uploaded_by: int
    filename: str
    original_filename: str
    file_size: int
    mime_type: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = []
    retention_category: Optional[str] = None
    retention_until: Optional[str] = None
    version: int
    previous_version_id: Optional[int] = None
    is_archived: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# --- Share link schemas ---

class ShareLinkCreate(BaseModel):
    name: str
    folder_ids: List[int] = []
    file_ids: List[int] = []
    password: Optional[str] = None
    expires_at: Optional[str] = None
    max_downloads: Optional[int] = None


class ShareLinkUpdate(BaseModel):
    is_active: Optional[bool] = None
    expires_at: Optional[str] = None
    max_downloads: Optional[int] = None


class ShareLinkOut(BaseModel):
    id: int
    company_id: int
    created_by: int
    share_token: str
    name: str
    folder_ids: List[int] = []
    file_ids: List[int] = []
    expires_at: Optional[str] = None
    max_downloads: Optional[int] = None
    download_count: int
    last_accessed: Optional[str] = None
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class AccessLogOut(BaseModel):
    id: int
    share_link_id: Optional[int] = None
    file_id: Optional[int] = None
    company_id: int
    action: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    accessed_at: str

    class Config:
        from_attributes = True


class RetentionAlertOut(BaseModel):
    file_id: int
    filename: str
    original_filename: str
    retention_category: Optional[str] = None
    retention_until: Optional[str] = None
    folder_id: int
    days_remaining: int


class RetentionSummaryOut(BaseModel):
    total_files: int
    permanent: int
    eight_years: int
    six_years: int
    three_years: int
    custom: int
    no_retention: int
    expiring_soon: int  # Within 90 days


class SharedFileOut(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    mime_type: Optional[str] = None
    description: Optional[str] = None


class SharedFolderOut(BaseModel):
    id: int
    name: str
    files: List[SharedFileOut] = []
