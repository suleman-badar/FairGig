from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


PlatformType = Literal[
    "Careem",
    "Bykea",
    "inDrive",
    "Foodpanda",
    "Cheetay",
    "Daraz",
    "Rozee",
    "Freelance_Upwork",
    "Freelance_Fiverr",
    "Freelance_Other",
    "Domestic",
    "Other",
]

VerificationStatus = Literal[
    "unsubmitted",
    "pending",
    "verified",
    "discrepancy",
    "unverifiable",
]

ReviewStatus = Literal["verified", "discrepancy", "unverifiable"]


class ShiftCreate(BaseModel):
    platform: PlatformType
    shift_date: date
    hours_worked: float = Field(ge=0)
    gross_earned: float = Field(ge=0)
    platform_deductions: float = Field(ge=0)
    net_received: float = Field(ge=0)
    notes: str | None = None


class ShiftUpdate(BaseModel):
    platform: PlatformType | None = None
    shift_date: date | None = None
    hours_worked: float | None = Field(default=None, ge=0)
    gross_earned: float | None = Field(default=None, ge=0)
    platform_deductions: float | None = Field(default=None, ge=0)
    net_received: float | None = Field(default=None, ge=0)
    notes: str | None = None


class ShiftOut(BaseModel):
    id: str
    worker_id: str
    platform: str
    shift_date: date
    hours_worked: Decimal
    gross_earned: Decimal
    platform_deductions: Decimal
    net_received: Decimal
    notes: str | None
    screenshot_filename: str | None
    verification_status: str
    verifier_id: str | None
    verifier_note: str | None
    verified_at: datetime | None
    created_at: datetime | None
    updated_at: datetime | None

    class Config:
        from_attributes = True


class ShiftCreateResponse(BaseModel):
    shift: ShiftOut
    warning: str | None = None


class BulkImportResponse(BaseModel):
    inserted: int
    errors: list[dict]


class VerificationReviewRequest(BaseModel):
    status: ReviewStatus
    note: str | None = None
