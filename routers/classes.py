from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

import crud, schemas, auth, models
from database import get_db

router = APIRouter(
    prefix="/classes",
    tags=["classes"],
)

@router.post("/", response_model=schemas.ClassSchedule)
def create_class(class_schedule: schemas.ClassScheduleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.require_admin)):
    return crud.create_class_schedule(db=db, class_schedule=class_schedule)

@router.get("/", response_model=List[schemas.ClassSchedule])
def read_classes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    return crud.get_class_schedules(db, skip=skip, limit=limit)

@router.get("/{class_id}", response_model=schemas.ClassSchedule)
def read_class(class_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_class = crud.get_class_schedule(db, class_id=class_id)
    if db_class is None:
        raise HTTPException(status_code=404, detail="Class not found")
    return db_class

@router.delete("/{class_id}", status_code=204)
def delete_class(class_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(auth.require_admin)):
    db_class = crud.delete_class_schedule(db, class_id=class_id)
    if db_class is None:
        raise HTTPException(status_code=404, detail="Class not found")
    return None

@router.post("/enrollments/", response_model=schemas.Enrollment)
def create_enrollment(enrollment: schemas.EnrollmentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    if current_user.role == models.RoleEnum.Student and current_user.player_id != enrollment.player_id:
        raise HTTPException(status_code=403, detail="Not authorized to enroll this player")

    # Validate player and class exist
    db_player = crud.get_player(db, enrollment.player_id)
    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")
    db_class = crud.get_class_schedule(db, enrollment.class_id)
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
        
    # Check for existing active/paused enrollment
    existing = db.query(models.Enrollment).filter(
        models.Enrollment.player_id == enrollment.player_id,
        models.Enrollment.class_id == enrollment.class_id,
        models.Enrollment.status != models.StatusEnum.Cancelled
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Player is already enrolled in this class")
        
    return crud.create_enrollment(db=db, enrollment=enrollment)

@router.get("/{class_id}/roster", response_model=List[schemas.Player])
def read_class_roster(class_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_class = crud.get_class_schedule(db, class_id)
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    return crud.get_class_roster(db, class_id)

@router.get("/player/{player_id}/enrollments", response_model=List[schemas.EnrollmentWithClass])
def get_player_enrollments(player_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    return crud.get_enrollments_for_player(db, player_id)

@router.put("/enrollments/{enrollment_id}", response_model=schemas.Enrollment)
def update_enrollment(enrollment_id: UUID, enrollment_update: schemas.EnrollmentUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_enrollment = crud.get_enrollment(db, enrollment_id)
    if not db_enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
        
    if current_user.role == models.RoleEnum.Student and current_user.player_id != db_enrollment.player_id:
        raise HTTPException(status_code=403, detail="Not authorized to manage this enrollment")
        
    return crud.update_enrollment(db, enrollment_id, enrollment_update)
