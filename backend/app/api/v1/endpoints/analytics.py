from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app import models
from app.database import get_db
from app.security import get_current_active_user

router = APIRouter()


@router.get("/student-performance")
def get_student_performance(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Get student performance analytics based on user role:
    - Mentor: See their students' performance
    - Admin: See all students under their mentors' performance
    - Others: Access denied
    """
    role = (current_user.role or "").lower()
    
    if role == "mentor":
        # Get mentor's students
        students = db.query(models.User).filter(
            models.User.mentor_id == current_user.id,
            models.User.role == "student"
        ).all()
        
        student_ids = [s.id for s in students]
        
    elif role == "admin":
        # Get all mentors under this admin
        mentors = db.query(models.User).filter(
            models.User.admin_id == current_user.id,
            models.User.role == "mentor"
        ).all()
        
        mentor_ids = [m.id for m in mentors]
        
        # Get all students under those mentors
        students = db.query(models.User).filter(
            models.User.mentor_id.in_(mentor_ids),
            models.User.role == "student"
        ).all() if mentor_ids else []
        
        student_ids = [s.id for s in students]
        
    else:
        raise HTTPException(status_code=403, detail="Access denied. Only mentors and admins can view analytics.")
    
    if not student_ids:
        return {
            "total_students": 0,
            "average_xp": 0,
            "average_streak": 0,
            "students": [],
            "xp_distribution": [],
            "completion_rate": 0
        }
    
    # Get detailed student data
    student_data = []
    total_xp = 0
    total_streak = 0
    
    for student in students:
        # Count challenges completed
        challenges_completed = db.query(func.count(models.UserChallenge.challenge_id)).filter(
            models.UserChallenge.user_id == student.id
        ).scalar() or 0
        
        # Count module progress
        default_modules_completed = db.query(func.count(models.ModuleProgress.qa_id)).filter(
            models.ModuleProgress.user_id == student.id
        ).scalar() or 0
        custom_modules_completed = db.query(func.count(models.CustomModuleProgress.question_id)).filter(
            models.CustomModuleProgress.user_id == student.id
        ).scalar() or 0
        modules_completed = default_modules_completed + custom_modules_completed
        
        # Get recent submissions (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_submissions = db.query(
            func.count(models.Submission.id).label('total'),
            func.sum(case((models.Submission.is_correct == True, 1), else_=0)).label('correct')
        ).filter(
            models.Submission.user_id == student.id,
            models.Submission.timestamp >= thirty_days_ago
        ).first()
        
        total_submissions = recent_submissions.total or 0
        correct_submissions = recent_submissions.correct or 0
        accuracy = (correct_submissions / total_submissions * 100) if total_submissions > 0 else 0
        
        student_data.append({
            "id": student.id,
            "username": student.username,
            "xp": student.xp,
            "streak": student.streak,
            "challenges_completed": challenges_completed,
            "modules_completed": modules_completed,
            "recent_accuracy": round(accuracy, 2),
            "total_submissions_30d": total_submissions
        })
        
        total_xp += student.xp
        total_streak += student.streak
    
    # Calculate averages
    num_students = len(students)
    avg_xp = total_xp / num_students if num_students > 0 else 0
    avg_streak = total_streak / num_students if num_students > 0 else 0
    
    # XP distribution for chart (group by ranges)
    xp_ranges = [
        {"range": "0-50", "count": 0},
        {"range": "51-100", "count": 0},
        {"range": "101-200", "count": 0},
        {"range": "201-500", "count": 0},
        {"range": "500+", "count": 0}
    ]
    
    for student in students:
        xp = student.xp
        if xp <= 50:
            xp_ranges[0]["count"] += 1
        elif xp <= 100:
            xp_ranges[1]["count"] += 1
        elif xp <= 200:
            xp_ranges[2]["count"] += 1
        elif xp <= 500:
            xp_ranges[3]["count"] += 1
        else:
            xp_ranges[4]["count"] += 1
    
    # Overall completion stats
    total_challenges = db.query(func.count(models.Challenge.id)).scalar() or 30
    total_possible_completions = num_students * total_challenges
    total_completions = sum(s["challenges_completed"] for s in student_data)
    completion_rate = (total_completions / total_possible_completions * 100) if total_possible_completions > 0 else 0
    
    return {
        "total_students": num_students,
        "average_xp": round(avg_xp, 2),
        "average_streak": round(avg_streak, 2),
        "students": student_data,
        "xp_distribution": xp_ranges,
        "completion_rate": round(completion_rate, 2)
    }


@router.get("/activity-timeline")
def get_activity_timeline(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Get daily activity timeline for students
    """
    role = (current_user.role or "").lower()
    
    if role == "mentor":
        student_ids = [s.id for s in db.query(models.User).filter(
            models.User.mentor_id == current_user.id,
            models.User.role == "student"
        ).all()]
    elif role == "admin":
        mentor_ids = [m.id for m in db.query(models.User).filter(
            models.User.admin_id == current_user.id,
            models.User.role == "mentor"
        ).all()]
        student_ids = [s.id for s in db.query(models.User).filter(
            models.User.mentor_id.in_(mentor_ids),
            models.User.role == "student"
        ).all()] if mentor_ids else []
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not student_ids:
        return {"timeline": []}
    
    # Get submissions grouped by date
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Challenge submissions
    daily_challenge_stats = db.query(
        func.date(models.Submission.timestamp).label('date'),
        func.count(models.Submission.id).label('total_submissions'),
        func.sum(case((models.Submission.is_correct == True, 1), else_=0)).label('correct_submissions')
    ).filter(
        models.Submission.user_id.in_(student_ids),
        models.Submission.timestamp >= start_date
    ).group_by(func.date(models.Submission.timestamp)).all()
    
    # Module completions
    daily_module_stats = db.query(
        func.date(models.ModuleProgress.completed_at).label('date'),
        func.count(models.ModuleProgress.qa_id).label('module_completions')
    ).filter(
        models.ModuleProgress.user_id.in_(student_ids),
        models.ModuleProgress.completed_at >= start_date
    ).group_by(func.date(models.ModuleProgress.completed_at)).all()

    # Custom module completions
    daily_custom_module_stats = db.query(
        func.date(models.CustomModuleProgress.completed_at).label('date'),
        func.count(models.CustomModuleProgress.question_id).label('module_completions')
    ).filter(
        models.CustomModuleProgress.user_id.in_(student_ids),
        models.CustomModuleProgress.completed_at >= start_date
    ).group_by(func.date(models.CustomModuleProgress.completed_at)).all()
    
    # Combine data by date
    date_data = {}
    
    for stat in daily_challenge_stats:
        date_data[stat.date] = {
            "date": stat.date if stat.date else "",
            "total_submissions": stat.total_submissions or 0,
            "correct_submissions": stat.correct_submissions or 0,
            "module_completions": 0
        }
    
    for stat in daily_module_stats:
        if stat.date in date_data:
            date_data[stat.date]["module_completions"] = stat.module_completions or 0
        else:
            date_data[stat.date] = {
                "date": stat.date if stat.date else "",
                "total_submissions": 0,
                "correct_submissions": 0,
                "module_completions": stat.module_completions or 0
            }

    for stat in daily_custom_module_stats:
        if stat.date in date_data:
            date_data[stat.date]["module_completions"] += stat.module_completions or 0
        else:
            date_data[stat.date] = {
                "date": stat.date if stat.date else "",
                "total_submissions": 0,
                "correct_submissions": 0,
                "module_completions": stat.module_completions or 0
            }
    
    # Build timeline sorted by date
    timeline = []
    for date in sorted(date_data.keys()):
        data = date_data[date]
        total = data["total_submissions"]
        timeline.append({
            "date": data["date"],
            "total_submissions": total,
            "correct_submissions": data["correct_submissions"],
            "module_completions": data["module_completions"],
            "accuracy": round((data["correct_submissions"] / total * 100) if total > 0 else 0, 2)
        })
    
    return {"timeline": timeline}
