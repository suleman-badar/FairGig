import uuid

from sqlalchemy import Column, Date, DateTime, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID

from database import Base


class Shift(Base):
    __tablename__ = "shifts"
    __table_args__ = {"schema": "earnings"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    worker_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)
    shift_date = Column(Date, nullable=False, index=True)
    hours_worked = Column(Numeric(4, 2), nullable=False)
    gross_earned = Column(Numeric(10, 2), nullable=False)
    platform_deductions = Column(Numeric(10, 2), nullable=False, default=0)
    net_received = Column(Numeric(10, 2), nullable=False)
    notes = Column(Text, nullable=True)

    screenshot_filename = Column(Text, nullable=True)
    screenshot_uploaded_at = Column(DateTime(timezone=True), nullable=True)
    verification_status = Column(String(20), nullable=False, default="unsubmitted", index=True)
    verifier_id = Column(UUID(as_uuid=True), nullable=True)
    verifier_note = Column(Text, nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
