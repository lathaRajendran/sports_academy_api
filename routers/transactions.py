from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

import crud, schemas, models, auth
from database import get_db

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)

@router.post("/", response_model=schemas.Transaction)
def record_transaction(transaction: schemas.TransactionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.require_admin)):
    player = crud.get_player(db, transaction.player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
        
    db_transaction = crud.create_transaction(db=db, transaction=transaction)
    return db_transaction

@router.get("/player/{player_id}", response_model=List[schemas.Transaction])
def get_player_transactions(player_id: UUID, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    return db.query(models.Transaction).filter(models.Transaction.player_id == player_id).order_by(models.Transaction.timestamp.desc()).all()
