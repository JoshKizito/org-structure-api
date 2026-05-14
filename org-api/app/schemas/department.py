from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip(v: str) -> str:
    return v.strip()


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Department name")
    parent_id: Optional[int] = Field(None, description="Parent department ID")

    @field_validator("name", mode="before")
    @classmethod
    def trim_name(cls, v: str) -> str:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("name must not be blank")
        return v


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    parent_id: Optional[int] = None

    @field_validator("name", mode="before")
    @classmethod
    def trim_name(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("name must not be blank")
        return v


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class DepartmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    parent_id: Optional[int]
    created_at: datetime


class EmployeeReadBrief(BaseModel):
    """Compact employee view embedded inside department tree responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    position: str
    hired_at: Optional[str] = None
    created_at: datetime

    @field_validator("hired_at", mode="before")
    @classmethod
    def coerce_date(cls, v: object) -> Optional[str]:
        if v is None:
            return None
        return str(v)


class DepartmentTree(BaseModel):
    """Recursive tree node returned by GET /departments/{id}."""
    model_config = ConfigDict(from_attributes=True)

    department: DepartmentRead
    employees: list[EmployeeReadBrief] = []
    children: list["DepartmentTree"] = []


# Needed so forward-reference resolves in Pydantic v2
DepartmentTree.model_rebuild()
