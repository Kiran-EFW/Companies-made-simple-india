import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database import Base


class DocumentType(str, enum.Enum):
    AADHAAR = "aadhaar"
    PAN_CARD = "pan_card"
    PASSPORT = "passport"
    UTILITY_BILL = "utility_bill"
    BANK_STATEMENT = "bank_statement"
    PHOTO = "photo"
    ADDRESS_PROOF = "address_proof"
    PITCH_DECK = "pitch_deck"
    OTHER = "other"


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    AI_VERIFIED = "ai_verified"
    PENDING_REVIEW = "pending_review"  # Moderate confidence — needs human review
    TEAM_VERIFIED = "team_verified"
    REJECTED = "rejected"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    director_id = Column(Integer, ForeignKey("directors.id"), nullable=True)

    doc_type = Column(Enum(DocumentType), nullable=False)
    file_path = Column(String, nullable=False)
    original_filename = Column(String, nullable=True)
    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING)
    extracted_data = Column(String, nullable=True)  # JSON string of OCR results
    rejection_reason = Column(String, nullable=True)

    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    verified_at = Column(DateTime, nullable=True)

    company = relationship("Company", back_populates="documents")
