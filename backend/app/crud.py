from sqlalchemy.orm import Session
from . import models, schemas

# --- User Functions ---

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

import secrets
import string

def generate_join_code(db: Session, length=8, max_attempts=10):
    """Generate a unique join code that doesn't already exist in the database"""
    alphabet = string.ascii_uppercase + string.digits
    for _ in range(max_attempts):
        code = ''.join(secrets.choice(alphabet) for _ in range(length))
        # Check if code already exists
        existing = db.query(models.User).filter(models.User.join_code == code).first()
        if not existing:
            return code
    # If we couldn't find a unique code after max_attempts, increase length
    return ''.join(secrets.choice(alphabet) for _ in range(length + 2))

def create_user(db: Session, user: schemas.UserCreate):
    from . import security
    hashed_password = security.get_password_hash(user.password)
    
    # ... Base user object remains same
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        role=user.role,
        # allow optional signup_date if present in user payload
        **({"signup_date": user.signup_date} if getattr(user, "signup_date", None) else {})
    )

    # --- HIERARCHY LINKING & CODE GENERATION ---
    
    # 1. Generate unique code for Admin/Mentor
    if user.role in ["admin", "mentor"]:
        db_user.join_code = generate_join_code(db)
    
    # 2. Linking logic based on provided code (which is passed in user.join_code field from signup)
    if user.role == "mentor" and user.join_code:
        # Here, user.join_code is the TARGET admin's code
        admin = db.query(models.User).filter(models.User.role == "admin", models.User.join_code == user.join_code).first()
        if admin:
            db_user.admin_id = admin.id
        else:
            # Optionally raise error if admin code invalid, but for now we proceed silently or set None
            pass

    elif user.role == "student" and user.join_code:
        # Here, user.join_code is the TARGET mentor's code
        mentor = db.query(models.User).filter(models.User.role == "mentor", models.User.join_code == user.join_code).first()
        if mentor:
            db_user.mentor_id = mentor.id

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    from . import security
    user = get_user_by_username(db, username=username)
    if not user:
        return None
    if not security.verify_password(password, user.hashed_password):
        return None
    return user

# --- Challenge Functions ---

def get_challenges(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Challenge).offset(skip).limit(limit).all()

def handle_submission(db: Session, user: models.User, challenge_id: int, submitted_answer: str):
    # 1. Check if challenge exists
    challenge = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    if not challenge:
        return {"success": False, "message": "Challenge not found."}

    # 2. Check if user already completed this challenge
    completion_record = db.query(models.UserChallenge).filter(
        models.UserChallenge.user_id == user.id,
        models.UserChallenge.challenge_id == challenge_id
    ).first()
    if completion_record:
        return {"success": False, "message": "You have already completed this challenge."}

    # 3. Check if the answer is correct
    is_correct = str(challenge.answer).strip().lower() == str(submitted_answer).strip().lower()

    # Record the submission attempt
    try:
        submission_record = models.Submission(
            user_id=user.id,
            challenge_id=challenge_id,
            answer=str(submitted_answer),
            is_correct=is_correct
        )
        db.add(submission_record)
    except Exception:
        # If Submission model/table is not present or any other DB error occurs,
        # continue with the main logic but report via rollback later if needed.
        db.rollback()

    if is_correct:
        # Award XP
        user.xp += 10
        # TODO: Implement more complex streak logic (e.g., based on timestamps)
        user.streak += 1

        # Mark challenge as completed
        new_completion = models.UserChallenge(user_id=user.id, challenge_id=challenge_id)
        db.add(new_completion)
        db.commit()
        db.refresh(user)
        return {"success": True, "message": "Correct! You've earned 10 XP."}
    else:
        # Incorrect answer - reset streak
        user.streak = 0
        db.commit()
        return {"success": False, "message": "Incorrect answer. Try again!"}

# --- Leaderboard Function ---

def get_leaderboard_users(db: Session, skip: int = 0, limit: int = 10, current_user: models.User | None = None):
    query = db.query(models.User)

    # Student-specific visibility: only students under the same mentor.
    if current_user and (current_user.role or "").lower() == "student":
        if current_user.mentor_id is not None:
            query = query.filter(
                models.User.role == "student",
                models.User.mentor_id == current_user.mentor_id,
            )
        else:
            # Unlinked students only see their own row.
            query = query.filter(models.User.id == current_user.id)

    # Mentor visibility: only their own students.
    elif current_user and (current_user.role or "").lower() == "mentor":
        query = query.filter(
            models.User.role == "student",
            models.User.mentor_id == current_user.id,
        )

    # Any other authenticated role (e.g., guest/parent) sees only self by default.
    elif current_user and (current_user.role or "").lower() != "admin":
        query = query.filter(models.User.id == current_user.id)

    return query.order_by(models.User.xp.desc()).offset(skip).limit(limit).all()

