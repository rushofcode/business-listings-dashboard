"""Pydantic models for validating listing input."""
import re
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

PHONE_RE = re.compile(r"^[0-9+()\\-\\s]{7,30}$")


class ListingIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    business_name: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    address: str = Field(min_length=1, max_length=500)
    phone: Optional[str] = Field(default=None, max_length=30)
    source: str = Field(min_length=1, max_length=100)

    @field_validator("phone", mode="before")
    @classmethod
    def phone_may_be_missing(cls, value):
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        return value

    @field_validator("phone")
    @classmethod
    def phone_looks_valid(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not PHONE_RE.match(value):
            raise ValueError("phone may only contain digits, spaces, +, -, ( ) and be 7–30 characters")
        return value


class BulkListingsRequest(BaseModel):
    listings: List[ListingIn] = Field(min_length=1, max_length=1000)
