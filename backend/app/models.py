# app/models.py

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from datetime import datetime

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # --- GAMIFICATION FIELDS ---
    xp = Column(Integer, default=0)
    streak = Column(Integer, default=0)
    # When the user signed up — used to calculate the daily challenge
    signup_date = Column(DateTime, default=datetime.utcnow)
    
    # --- ROLES & RELATIONSHIPS ---
    role = Column(String, default="student")  # student, parent, mentor, admin
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    child_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    join_code = Column(String, unique=True, nullable=True)

    # Hierarchical Relationships
    # A mentor has students
    students = relationship("User", backref=backref("mentor", remote_side=[id]), foreign_keys=[mentor_id])
    
    # An admin has mentors
    mentors = relationship("User", backref=backref("admin", remote_side=[id]), foreign_keys=[admin_id])

    challenges_completed = relationship("UserChallenge", back_populates="user")
    announcements = relationship("Announcement", back_populates="mentor")

class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    # MODIFIED: Changed 'description' to 'question' to match schemas.py
    question = Column(String)
    category = Column(String)
    answer = Column(String)
    is_active = Column(Boolean, default=True, nullable=False, server_default='1')

    # NEW: Added the missing relationship back to the UserChallenge table
    users_completed = relationship("UserChallenge", back_populates="challenge")

# --- ASSOCIATION TABLE ---
# This table links users to the challenges they have completed.

# --- SUBMISSION TABLE ---
# This table tracks each user's answer attempt, correctness, and timestamp.
from sqlalchemy import DateTime
from datetime import datetime

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    challenge_id = Column(Integer, ForeignKey("challenges.id"))
    answer = Column(String)
    is_correct = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Note: we don't strictly need back_populates unless we navigate from User to All Submissions
    user = relationship("User")
    challenge = relationship("Challenge")

class UserChallenge(Base):
    __tablename__ = "user_challenges"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), primary_key=True)
    user = relationship("User", back_populates="challenges_completed")
    challenge = relationship("Challenge", back_populates="users_completed")

# --- MODULES PROGRESS TABLE ---
# Tracks which module QAs a user has completed correctly to avoid re-awarding XP
class ModuleProgress(Base):
    __tablename__ = "module_progress"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    level = Column(String, primary_key=True)  # beginner | intermediate | expert
    qa_id = Column(Integer, primary_key=True)  # 1..20 within each level
    completed_at = Column(DateTime, default=datetime.utcnow)

# --- ANNOUNCEMENTS TABLE ---
class Announcement(Base):
    __tablename__ = "announcements"
    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    mentor = relationship("User", back_populates="announcements")

# --- CUSTOM MODULES (generated from PDF) ---
from sqlalchemy import JSON

class CustomModule(Base):
    __tablename__ = "custom_modules"
    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String, index=True)
    subject    = Column(String, default="Custom")
    level      = Column(String, default="beginner")   # beginner | intermediate | expert
    mentor_id  = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    questions = relationship("CustomModuleQuestion", back_populates="module",
                             cascade="all, delete-orphan", lazy="select")
    mentor    = relationship("User")

class CustomModuleQuestion(Base):
    __tablename__ = "custom_module_questions"
    id            = Column(Integer, primary_key=True, index=True)
    module_id     = Column(Integer, ForeignKey("custom_modules.id"))
    question_type = Column(String)        # mcq | true_false | fill_blank
    question_text = Column(String)
    options       = Column(JSON, nullable=True)  # list[str] for MCQ / T-F
    correct_answer= Column(String)
    explanation   = Column(String, default="")

    module = relationship("CustomModule", back_populates="questions")


# --- CUSTOM MODULE PROGRESS TABLE ---
# Tracks which custom module questions a user has completed correctly.
class CustomModuleProgress(Base):
    __tablename__ = "custom_module_progress"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    module_id = Column(Integer, ForeignKey("custom_modules.id"), primary_key=True)
    question_id = Column(Integer, ForeignKey("custom_module_questions.id"), primary_key=True)
    completed_at = Column(DateTime, default=datetime.utcnow)