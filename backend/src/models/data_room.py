from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Boolean, ForeignKey
from datetime import datetime, timezone
from src.database import Base


class DataRoomFolder(Base):
    __tablename__ = "data_room_folders"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("data_room_folders.id"), nullable=True)
    folder_type = Column(String, nullable=True)
    # Standard folders: INCORPORATION, COMPLIANCE, FINANCIALS, AGREEMENTS,
    # CAP_TABLE, BOARD_MEETINGS, IP, HR, TAX, CUSTOM
    sort_order = Column(Integer, default=0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class DataRoomFile(Base):
    __tablename__ = "data_room_files"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    folder_id = Column(Integer, ForeignKey("data_room_folders.id"), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, default=0)  # bytes
    mime_type = Column(String, nullable=True)

    description = Column(Text, nullable=True)
    tags = Column(JSON, default=list)  # ["legal", "compliance", etc.]

    # Data retention
    retention_category = Column(String, nullable=True)
    # Categories: PERMANENT (statutory registers), 8_YEARS (books of accounts - Sec 128),
    # 6_YEARS (tax records), 3_YEARS (DPDP), CUSTOM
    retention_until = Column(DateTime, nullable=True)

    # Version tracking
    version = Column(Integer, default=1)
    previous_version_id = Column(Integer, ForeignKey("data_room_files.id"), nullable=True)

    is_archived = Column(Boolean, default=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class DataRoomShareLink(Base):
    __tablename__ = "data_room_share_links"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    share_token = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)  # "Series A Due Diligence", "Auditor Access"

    # Access control
    folder_ids = Column(JSON, default=list)  # Which folders are shared
    file_ids = Column(JSON, default=list)  # Specific files (if not whole folders)
    password_hash = Column(String, nullable=True)  # Optional password protection

    # Expiry & tracking
    expires_at = Column(DateTime, nullable=True)
    max_downloads = Column(Integer, nullable=True)
    download_count = Column(Integer, default=0)
    last_accessed = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class DataRoomAccessLog(Base):
    __tablename__ = "data_room_access_logs"

    id = Column(Integer, primary_key=True, index=True)
    share_link_id = Column(Integer, ForeignKey("data_room_share_links.id"), nullable=True)
    file_id = Column(Integer, ForeignKey("data_room_files.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    action = Column(String, nullable=False)  # view, download, share_link_access
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    accessed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
