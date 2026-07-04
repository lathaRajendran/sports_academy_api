from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

import crud, schemas, auth, models
from database import get_db

router = APIRouter(
    prefix="/coaches",
    tags=["coaches"],
)

@router.post("/", response_model=schemas.Coach)
def create_coach(coach: schemas.CoachCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.require_admin)):
    return crud.create_coach(db=db, coach=coach)

@router.get("/", response_model=List[schemas.Coach])
def read_coaches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    return crud.get_coaches(db, skip=skip, limit=limit)

@router.get("/{coach_id}", response_model=schemas.Coach)
def read_coach(coach_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_coach = crud.get_coach(db, coach_id=coach_id)
    if db_coach is None:
        raise HTTPException(status_code=404, detail="Coach not found")
    return db_coach
