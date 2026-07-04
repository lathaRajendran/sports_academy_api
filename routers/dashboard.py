from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

import models, auth
from database import get_db

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
)

@router.get("/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    # 1. Active Players
    active_players = db.query(models.Player).filter(models.Player.status == models.StatusEnum.Active).count()
    
    # 2. Upcoming Classes
    # Just return total classes for now
    upcoming_classes = db.query(models.ClassSchedule).count()
    
    # 3. Attendance
    total_attendance = db.query(models.Attendance).count()
    attended = db.query(models.Attendance).filter(models.Attendance.status == models.AttendanceStatusEnum.Attended).count()
    attendance_rate = 0
    if total_attendance > 0:
        attendance_rate = round((attended / total_attendance) * 100, 1)
        
    # 4. Outstanding Balances (Players with negative balance)
    outstanding_balances = db.query(func.sum(models.Player.current_balance)).filter(models.Player.current_balance < 0).scalar() or 0.0
    
    # 5. Revenue
    revenue = db.query(func.sum(models.Transaction.amount)).filter(models.Transaction.type == models.TransactionTypeEnum.Credit_Purchase).scalar() or 0.0
    
    # 6. Enrollment
    active_enrollments = db.query(models.Enrollment).filter(models.Enrollment.status == models.StatusEnum.Active).count()
    
    return {
        "active_players": active_players,
        "upcoming_classes": upcoming_classes,
        "attendance_rate": attendance_rate,
        "outstanding_balances": abs(float(outstanding_balances)),
        "revenue": float(revenue),
        "active_enrollments": active_enrollments
    }
