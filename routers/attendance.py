from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

import crud, schemas, models, auth
from database import get_db

router = APIRouter(
    prefix="/attendance",
    tags=["attendance"],
)

@router.post("/", response_model=schemas.Attendance)
def mark_attendance(attendance: schemas.AttendanceCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.require_admin)):
    # Verify player exists
    player = crud.get_player(db, attendance.player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
        
    # State-machine logic
    final_status = attendance.status
    
    # Get class cost
    db_class = crud.get_class_schedule(db, attendance.class_id)
    class_fee = db_class.fee_per_class if db_class else 0
    
    if attendance.status == models.AttendanceStatusEnum.Attended:
        player.current_balance -= class_fee
    elif attendance.status == models.AttendanceStatusEnum.Missed:
        final_status = models.AttendanceStatusEnum.Makeup
        # Refund happens by simply NOT deducting the fee for Missed/Makeup, or if they pre-paid.
        # Since it's a wallet system, we just don't deduct if they missed.
    
    # Create the attendance record
    db_attendance = models.Attendance(
        player_id=attendance.player_id,
        class_id=attendance.class_id,
        date=attendance.date,
        status=final_status
    )
    
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    
    return db_attendance

@router.get("/player/{player_id}", response_model=List[schemas.Attendance])
def get_player_attendance(player_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    if current_user.role == models.RoleEnum.Student and current_user.player_id != player_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this player's attendance")
        
    return db.query(models.Attendance).filter(models.Attendance.player_id == player_id).order_by(models.Attendance.date.desc()).all()

