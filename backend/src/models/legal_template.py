from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from datetime import datetime, timezone
from src.database import Base


class LegalDocument(Base):
    __tablename__ = "legal_documents"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    template_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    status = Column(String, default="draft")
    version = Column(Integer, default=1)

    clauses_config = Column(JSON, default=dict)
    generated_html = Column(Text, nullable=True)
    generated_content = Column(JSON, nullable=True)
    parties = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
