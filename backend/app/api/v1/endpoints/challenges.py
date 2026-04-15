from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
from datetime import date
import re

from app import crud, models, schemas
from app.database import get_db
from app.security import get_current_active_user, get_current_user_optional

router = APIRouter()


@router.get("/", response_model=List[schemas.Challenge])
def read_challenges(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User | None = Depends(get_current_user_optional),
):
    """
    Retrieve only the challenges for the authenticated user's current nth day.
    The cycle length is based on the highest active configured day number.
    Example: if challenges exist up to Day 31, recycle after Day 31.
    """
    active_titles = db.query(models.Challenge.title).filter(models.Challenge.is_active == True).all()
    max_configured_day = 1
    for (title,) in active_titles:
        m = re.search(r"Day\s*(\d+)", title or "", re.IGNORECASE)
        if not m:
            continue
        try:
            day_num = int(m.group(1))
        except Exception:
            continue
        if day_num > max_configured_day:
            max_configured_day = day_num

    # Calculate days since signup (1-based)
    # If no user (anonymous) or missing signup_date, default to day 1
    if not current_user or not getattr(current_user, "signup_date", None):
        nth = 1
    else:
        days_since = (date.today() - current_user.signup_date.date()).days + 1
        nth = ((days_since - 1) % max_configured_day) + 1

    all_challenges = crud.get_challenges(db, skip=skip, limit=limit*5)
    filtered = []
    seen_keys = set()
    for c in all_challenges:
        if not getattr(c, 'is_active', True):
            continue
        m = re.search(r"Day\s*(\d+)", c.title or "", re.IGNORECASE)
        if m:
            try:
                day_num = int(m.group(1))
            except Exception:
                continue
            if day_num == nth:
                key = ((c.title or "").strip().lower(), (c.question or "").strip().lower())
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                filtered.append(c)
    return filtered

@router.post("/{challenge_id}/submit")
def submit_challenge_answer(
    challenge_id: int,
    submission: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Submit an answer for a challenge.
    """
    # MODIFIED: Pass the answer string from the submission object, not the object itself.
    # accept flexible body shapes (frontend may send {answer} or nested payloads)
    answer = None
    if isinstance(submission, dict):
        # try common keys
        answer = submission.get('answer') or submission.get('answer_text') or submission.get('answerValue')

    if answer is None:
        raise HTTPException(status_code=400, detail="Missing 'answer' in request body")

    result = crud.handle_submission(
        db=db,
        user=current_user,
        challenge_id=challenge_id,
        submitted_answer=answer
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result
