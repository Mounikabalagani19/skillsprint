# app/schemas.py

from pydantic import BaseModel, ConfigDict, field_validator # <-- Import ConfigDict
from typing import List, Optional
from datetime import datetime

# --- Challenge Schemas ---
class ChallengeBase(BaseModel):
    title: str
    category: str
    question: str

class ChallengeCreate(ChallengeBase):
    answer: str

class Challenge(ChallengeBase):
    id: int
    day: Optional[int] = None

    # This is the new Pydantic V2 syntax
    model_config = ConfigDict(from_attributes=True)

# --- Submission Schemas ---
# Payload accepted when submitting an answer
class SubmissionCreate(BaseModel):
    answer: str

# Full Submission representation stored in DB (for responses or history)
class Submission(BaseModel):
    user_id: int
    challenge_id: int
    answer: str
    is_correct: bool
    timestamp: Optional[str] = None

# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

    # bcrypt only supports up to 72 bytes; enforce a safe limit
    @field_validator("password")
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password too long: must be 72 bytes or fewer")
        return v

class User(UserBase):
    id: int
    xp: int
    streak: int
    signup_date: Optional[datetime] = None

    # This is the new Pydantic V2 syntax
    model_config = ConfigDict(from_attributes=True)

# --- Token Schema ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None