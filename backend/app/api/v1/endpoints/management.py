from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import io
from pypdf import PdfReader
import re

from app import models, schemas, crud
from app.database import get_db
from app.security import get_current_user
import random as _random
from app.nlp_generator import generate_questions

router = APIRouter()

# --- HELPER: ROLE CHECK ---
def check_mentor_or_admin(user: models.User):
    if user.role not in ["mentor", "admin"]:
        raise HTTPException(status_code=403, detail="Manager access required")

# --- MENTOR: GET STUDENTS ---
@router.get("/mentor/students", response_model=List[schemas.User])
def get_mentor_students(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "mentor":
        raise HTTPException(status_code=403, detail="Mentor access required")
    
    return db.query(models.User).filter(models.User.mentor_id == current_user.id).all()

# --- ADMIN: GET STATS ---
@router.get("/admin/stats")
def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get all mentors under this admin
    mentors = db.query(models.User).filter(models.User.admin_id == current_user.id).all()
    mentor_map = {m.id: m.username for m in mentors}
    mentor_ids = list(mentor_map.keys())
    
    # Get all students under these mentors
    students = db.query(models.User).filter(models.User.mentor_id.in_(mentor_ids)).all()
    
    student_details = []
    for s in students:
        student_details.append({
            "id": s.id,
            "username": s.username,
            "email": s.email,
            "xp": s.xp,
            "streak": s.streak,
            "mentor_name": mentor_map.get(s.mentor_id, "Unknown")
        })
    
    return {
        "mentor_count": len(mentors),
        "student_count": len(students),
        "total_xp": sum(s.xp for s in students),
        "average_streak": sum(s.streak for s in students) / len(students) if students else 0,
        "students": student_details
    }

# --- MENTOR: BATCH UPLOAD CHALLENGES ---
@router.post("/mentor/challenges")
def batch_upload_challenges(
    challenges: List[schemas.ChallengeCreate],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "mentor":
        raise HTTPException(status_code=403, detail="Mentor access required")
    
    new_challenges = []
    for c in challenges:
        db_challenge = models.Challenge(**c.dict())
        db.add(db_challenge)
        new_challenges.append(db_challenge)
    
    db.commit()
    return {"status": "success", "count": len(new_challenges)}

# --- MENTOR: PDF TO MODULE (NLP-based) ---
@router.post("/mentor/modules/pdf")
async def create_module_from_pdf(
    file: UploadFile = File(...),
    level: str = Form("beginner"),
    module_name: str = Form("Custom Module"),
    num_questions: int = Form(15),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Extract text from a PDF and auto-generate Q&A questions using NLP.
    Returns a preview of generated questions — does NOT save to DB yet.
    Call  POST /mentor/modules/save  to persist them.
    """
    if current_user.role != "mentor":
        raise HTTPException(status_code=403, detail="Mentor access required")

    content = await file.read()
    try:
        pdf = PdfReader(io.BytesIO(content))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read PDF file")

    # Collect per-page text (skip blank pages)
    pages_text = []
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text and len(page_text.strip()) > 50:
            pages_text.append(page_text)

    if not pages_text:
        raise HTTPException(
            status_code=400,
            detail="PDF has very little extractable text. "
                   "Try a text-based PDF rather than a scanned image."
        )

    # ── NLP generation — generate from each page, then enforce 5:4:1 ratio ──
    clamped_total = max(5, min(num_questions, 30))

    # Always request at least 10 questions per page so every call covers at
    # least one full 5:4:1 cycle (the pattern repeats every 10 slots).
    all_questions: list[dict] = []
    for page_text in pages_text:
        all_questions.extend(generate_questions(page_text, num_questions=10))

    # Remove duplicates (same question text) while preserving order
    seen_q: set[str] = set()
    deduped: list[dict] = []
    for q in all_questions:
        key = q["question"].strip().lower()
        if key not in seen_q:
            seen_q.add(key)
            deduped.append(q)

    # Compute per-type targets for the requested total using 5:4:1 pattern
    _pattern = ["mcq"] * 5 + ["fill_blank"] * 4 + ["true_false"]
    mcq_t = fill_t = tf_t = 0
    for idx in range(clamped_total):
        slot = _pattern[idx % len(_pattern)]
        if slot == "mcq":
            mcq_t += 1
        elif slot == "fill_blank":
            fill_t += 1
        else:
            tf_t += 1

    by_type: dict[str, list[dict]] = {"mcq": [], "fill_blank": [], "true_false": []}
    for q in deduped:
        bucket = q.get("type", "")
        if bucket in by_type:
            by_type[bucket].append(q)

    _random.shuffle(by_type["mcq"])
    _random.shuffle(by_type["fill_blank"])
    _random.shuffle(by_type["true_false"])

    questions = (
        by_type["mcq"][:mcq_t]
        + by_type["fill_blank"][:fill_t]
        + by_type["true_false"][:tf_t]
    )
    _random.shuffle(questions)
    questions = questions[:clamped_total]

    if not questions:
        raise HTTPException(
            status_code=400,
            detail="Could not extract enough content to generate questions. "
                   "Make sure the PDF contains plain educational text."
        )

    return {
        "module_name":       module_name,
        "level":             level,
        "questions_parsed":  len(questions),
        "questions":         questions,          # full list for preview
        "preview":           questions[:3],      # first 3 for quick look
    }


# --- MENTOR: SAVE GENERATED MODULE ---
@router.post("/mentor/modules/save")
def save_module(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Persist an approved module (returned from /pdf endpoint) to the database.
    Payload: { module_name, level, subject, questions: [...] }
    """
    if current_user.role != "mentor":
        raise HTTPException(status_code=403, detail="Mentor access required")

    questions = payload.get("questions", [])
    if not questions:
        raise HTTPException(status_code=400, detail="No questions provided")

    module = models.CustomModule(
        name=payload.get("module_name", "Custom Module"),
        subject=payload.get("subject", "Custom"),
        level=payload.get("level", "beginner"),
        mentor_id=current_user.id,
    )
    db.add(module)
    db.flush()  # get module.id before adding questions

    for q in questions:
        db_q = models.CustomModuleQuestion(
            module_id=module.id,
            question_type=q.get("type", "mcq"),
            question_text=q.get("question", ""),
            options=q.get("options", []),
            correct_answer=q.get("answer", ""),
            explanation=q.get("explanation", ""),
        )
        db.add(db_q)

    db.commit()
    db.refresh(module)
    return {
        "status":    "saved",
        "module_id": module.id,
        "name":      module.name,
        "questions_saved": len(questions),
    }


# --- LIST CUSTOM MODULES (mentor sees own; students see all) ---
@router.get("/modules/custom")
def list_custom_modules(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Return all custom modules visible to the current user."""
    if current_user.role == "mentor":
        modules = db.query(models.CustomModule).filter(
            models.CustomModule.mentor_id == current_user.id
        ).all()
    else:
        modules = db.query(models.CustomModule).all()

    return [
        {
            "id":         m.id,
            "name":       m.name,
            "subject":    m.subject,
            "level":      m.level,
            "mentor_id":  m.mentor_id,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "question_count": len(m.questions),
        }
        for m in modules
    ]


# --- GET SINGLE CUSTOM MODULE WITH QUESTIONS ---
@router.get("/modules/custom/{module_id}")
def get_custom_module(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    module = db.query(models.CustomModule).filter(
        models.CustomModule.id == module_id
    ).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    return {
        "id":      module.id,
        "name":    module.name,
        "subject": module.subject,
        "level":   module.level,
        "questions": [
            {
                "id":            q.id,
                "type":          q.question_type,
                "question":      q.question_text,
                "options":       q.options or [],
                "answer":        q.correct_answer,
                "explanation":   q.explanation,
            }
            for q in module.questions
        ],
    }


# --- MENTOR: LIST ALL CHALLENGES (admin/management view) ---
@router.get("/mentor/challenges/all")
def list_all_challenges(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    check_mentor_or_admin(current_user)
    all_c = db.query(models.Challenge).order_by(models.Challenge.id.asc()).all()
    result = []
    for c in all_c:
        m = re.search(r"Day\s*(\d+)", c.title or "", re.IGNORECASE)
        day_num = int(m.group(1)) if m else 0
        result.append({
            "id":       c.id,
            "title":    c.title,
            "question": c.question,
            "category": c.category,
            "answer":   c.answer,
            "day":      day_num,
            "is_active": bool(c.is_active),
        })
    result.sort(key=lambda x: (x["day"], x["id"]))
    return result

    # --- MENTOR: TOGGLE CHALLENGE ACTIVE STATE ---
    @router.patch("/mentor/challenges/{challenge_id}/toggle")
    def toggle_challenge_active(
        challenge_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
    ):
        check_mentor_or_admin(current_user)
        c = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
        if not c:
            raise HTTPException(status_code=404, detail="Challenge not found")
        c.is_active = not bool(c.is_active)
        db.commit()
        return {"id": c.id, "is_active": bool(c.is_active)}


# --- MENTOR: CREATE SINGLE CHALLENGE MANUALLY ---
@router.post("/mentor/challenges/single")
def create_single_challenge(
    data: schemas.ChallengeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    check_mentor_or_admin(current_user)
    c = models.Challenge(**data.dict())
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"status": "created", "id": c.id}


# --- MENTOR: UPDATE A CHALLENGE ---
@router.put("/mentor/challenges/{challenge_id}")
def update_challenge(
    challenge_id: int,
    data: schemas.ChallengeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    check_mentor_or_admin(current_user)
    c = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Challenge not found")
    c.title    = data.title
    c.question = data.question
    c.category = data.category
    c.answer   = data.answer
    db.commit()
    db.refresh(c)
    return {"status": "updated", "id": c.id}


# --- MENTOR: DELETE A CHALLENGE ---
@router.delete("/mentor/challenges/{challenge_id}")
def delete_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    check_mentor_or_admin(current_user)
    c = db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Challenge not found")
    db.query(models.Submission).filter(models.Submission.challenge_id == challenge_id).delete(synchronize_session=False)
    db.query(models.UserChallenge).filter(models.UserChallenge.challenge_id == challenge_id).delete(synchronize_session=False)
    db.delete(c)
    db.commit()
    return {"status": "deleted"}


# --- DELETE CUSTOM MODULE ---
@router.delete("/modules/custom/{module_id}")
def delete_custom_module(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "mentor":
        raise HTTPException(status_code=403, detail="Mentor access required")
    module = db.query(models.CustomModule).filter(
        models.CustomModule.id == module_id,
        models.CustomModule.mentor_id == current_user.id,
    ).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    db.delete(module)
    db.commit()
    return {"status": "deleted"}
