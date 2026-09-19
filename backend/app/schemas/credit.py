from typing import Optional
from pydantic import BaseModel, ConfigDict


class PersonSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tmdb_id: int
    name: str
    profile_path: Optional[str] = None


class CreditSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    credit_type: str  # "cast" or "crew"
    character: Optional[str] = None
    department: Optional[str] = None
    job: Optional[str] = None
    person: PersonSummary

