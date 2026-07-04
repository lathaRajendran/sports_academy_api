from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import date

import crud, schemas, auth, models
from database import get_db

router = APIRouter(
    prefix="/players",
    tags=["players"],
)

@router.post("/", response_model=schemas.Player)
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.require_admin)):
    return crud.create_player(db=db, player=player)

@router.post("/register", response_model=schemas.Player)
def register_player(registration: schemas.PlayerRegister, db: Session = Depends(get_db), current_user: models.User = Depends(auth.require_admin)):
    # 1. Validate class
    db_class = crud.get_class_schedule(db, registration.class_id)
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
        
    # Minimum payment check
    min_payment = float(db_class.fee_per_class) * 10 if db_class.fee_per_class else 0.0
    if registration.initial_payment < min_payment:
        raise HTTPException(status_code=400, detail=f"Initial payment must be at least ${min_payment:.2f} for this class")
        
    # 2. Create Player
    # Extract player base fields
    player_data = registration.model_dump(exclude={'class_id', 'initial_payment'})
    db_player = crud.create_player(db=db, player=schemas.PlayerCreate(**player_data))
    
    # 3. Create Enrollment
    enrollment = schemas.EnrollmentCreate(
        player_id=db_player.player_id,
        class_id=registration.class_id,
        start_date=date.today(),
        status=models.StatusEnum.Active
    )
    crud.create_enrollment(db=db, enrollment=enrollment)
    
    # 4. Create Transaction
    transaction = schemas.TransactionCreate(
        player_id=db_player.player_id,
        amount=registration.initial_payment,
        type=models.TransactionTypeEnum.Credit_Purchase,
        payment_method=registration.payment_method
    )
    crud.create_transaction(db=db, transaction=transaction)
    
    # Refresh and return
    db.refresh(db_player)
    return db_player

@router.get("/", response_model=List[schemas.Player])
def read_players(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    if current_user.role == models.RoleEnum.Student:
        if current_user.player_id:
            db_player = crud.get_player(db, current_user.player_id)
            return [db_player] if db_player else []
        return []
    return crud.get_players(db, skip=skip, limit=limit)

@router.get("/{player_id}", response_model=schemas.Player)
def read_player(player_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    if current_user.role == models.RoleEnum.Student and current_user.player_id != player_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this player")
    
    db_player = crud.get_player(db, player_id=player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return db_player

@router.patch("/{player_id}", response_model=schemas.Player)
def update_player(player_id: UUID, player: schemas.PlayerUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    if current_user.role == models.RoleEnum.Student and current_user.player_id != player_id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this player")
        
    db_player = crud.update_player(db, player_id=player_id, player_update=player)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return db_player

@router.delete("/{player_id}", status_code=204)
def delete_player(player_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(auth.require_admin)):
    db_player = crud.delete_player(db, player_id=player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return None

@router.post("/{player_id}/reminders")
def send_payment_reminder(player_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(auth.require_admin)):
    player = crud.get_player(db, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    if player.current_balance >= 0:
        return {"message": "Player does not have a negative balance."}
        
    # Simulate sending an email reminder
    print(f"SIMULATED EMAIL: Reminder sent to {player.email} regarding outstanding balance of ${abs(float(player.current_balance))}")
    return {"message": "Payment reminder email sent successfully"}
