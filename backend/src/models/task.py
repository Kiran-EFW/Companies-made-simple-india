import enum
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.database import Base


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_ON_USER = "waiting_on_user"
    WAITING_ON_TEAM = "waiting_on_team"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    result = Column(JSON, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    company = relationship("Company", back_populates="tasks")


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String, nullable=False)
    message = Column(String, nullable=False)
    level = Column(String, default="INFO")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    company = relationship("Company", back_populates="logs")
