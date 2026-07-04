from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import pandas as pd
import io
import math

import crud, schemas, models
from database import get_db

router = APIRouter(
    prefix="/import",
    tags=["import"],
)

def safe_int(val):
    if pd.isna(val):
        return 0
    try:
        return int(val)
    except:
        return 0

def safe_float(val):
    if pd.isna(val):
        return 0.0
    try:
        return float(val)
    except:
        return 0.0

def safe_str(val):
    if pd.isna(val):
        return None
    return str(val).strip()

@router.post("/")
async def upload_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(('.csv', '.xlsx')):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload CSV or Excel.")

    contents = await file.read()
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")

    # Expected columns:
    # Class Name, Class Ages, Player Age, Skill, Gender, Parent Name,
    # Payment Date, Payment Amount, Class Attended, Class Cost, Account Balance, Channel

    for index, row in df.iterrows():
        class_name = safe_str(row.get('Class Name'))
        class_ages = safe_str(row.get('Class Ages'))
        player_age = safe_int(row.get('Player Age'))
        skill = safe_str(row.get('Skill'))
        gender = safe_str(row.get('Gender'))
        parent_name = safe_str(row.get('Parent Name'))
        payment_date_raw = row.get('Payment Date')
        payment_amount = safe_float(row.get('Payment Amount'))
        class_attended = safe_int(row.get('Class Attended'))
        class_cost = safe_float(row.get('Class Cost'))
        account_balance = safe_float(row.get('Account Balance'))
        channel = safe_str(row.get('Channel'))

        if not parent_name:
            continue # Parent name is required
            
        # 1. Class Creation
        db_class = None
        if class_name:
            db_class = db.query(models.ClassSchedule).filter(models.ClassSchedule.class_name == class_name).first()
            if not db_class:
                db_class = models.ClassSchedule(
                    class_name=class_name,
                    target_ages=class_ages,
                    fee_per_class=class_cost
                )
                db.add(db_class)
                db.commit()
                db.refresh(db_class)

        # 2. Player/Parent Creation
        skill_enum = None
        if skill and skill.capitalize() in [s.value for s in models.SkillLevelEnum]:
            skill_enum = models.SkillLevelEnum(skill.capitalize())
            
        gender_enum = None
        if gender and gender.capitalize() in [g.value for g in models.GenderEnum]:
            gender_enum = models.GenderEnum(gender.capitalize())

        # Check if player already exists by parent name and age
        db_player = db.query(models.Player).filter(
            models.Player.parent_name == parent_name,
            models.Player.age == player_age
        ).first()

        if not db_player:
            db_player = models.Player(
                parent_name=parent_name,
                age=player_age,
                skill_level=skill_enum,
                gender=gender_enum,
                current_balance=account_balance,
                channel=channel
            )
            db.add(db_player)
            db.commit()
            db.refresh(db_player)
        else:
            db_player.current_balance = account_balance
            db.commit()

        # 3. Financials
        if payment_amount > 0:
            payment_date = None
            if not pd.isna(payment_date_raw):
                try:
                    payment_date = pd.to_datetime(payment_date_raw).to_pydatetime()
                except:
                    pass
            
            # Check if transaction exists
            existing_tx = db.query(models.Transaction).filter(
                models.Transaction.player_id == db_player.player_id,
                models.Transaction.amount == payment_amount
            ).first()
            
            if not existing_tx:
                db_tx = models.Transaction(
                    player_id=db_player.player_id,
                    amount=payment_amount,
                    type=models.TransactionTypeEnum.Credit_Purchase,
                    payment_method=models.PaymentMethodEnum.Cash, # default
                )
                if payment_date:
                    db_tx.timestamp = payment_date
                db.add(db_tx)
                db.commit()

        # 4. Attendance & Credits
        # If class cost is > 0, we can figure out purchased credits: payment / class_cost
        purchased_credits = 0
        if class_cost > 0 and payment_amount > 0:
            purchased_credits = int(payment_amount // class_cost)
            
        # Update available credits
        db_player.available_credits = purchased_credits - class_attended
        db.commit()
        
    return {"message": "Data imported successfully"}
