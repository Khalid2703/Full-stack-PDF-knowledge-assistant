"""
Pydantic schemas for User-related requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema with common fields"""
    # Use plain string for email here and validate/normalize in the service layer
    email: str
    name: str = Field(..., min_length=2, max_length=255)
    organization: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login"""
    email: str
    password: str


class UserResponse(UserBase):
    """Schema for user response (excludes password)"""
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded token data"""
    user_id: Optional[int] = None
    email: Optional[str] = None
