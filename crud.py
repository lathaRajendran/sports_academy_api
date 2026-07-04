from sqlalchemy.orm import Session
from uuid import UUID
import models, schemas
from decimal import Decimal

# --- Players ---

def get_player(db: Session, player_id: UUID):
    return db.query(models.Player).options(
        joinedload(models.Player.enrollments).joinedload(models.Enrollment.class_schedule),
        joinedload(models.Player.attendances)
    ).filter(models.Player.player_id == player_id).first()

from sqlalchemy.orm import Session, joinedload

def get_players(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Player).options(
        joinedload(models.Player.enrollments).joinedload(models.Enrollment.class_schedule),
        joinedload(models.Player.attendances)
    ).offset(skip).limit(limit).all()

def create_player(db: Session, player: schemas.PlayerCreate):
    db_player = models.Player(**player.model_dump())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

def update_player(db: Session, player_id: UUID, player_update: schemas.PlayerUpdate):
    db_player = get_player(db, player_id)
    if db_player:
        # Check if email is changing
        new_email = player_update.email
        old_email = db_player.email
        
        for key, value in player_update.model_dump(exclude_unset=True).items():
            setattr(db_player, key, value)
            
        # Update user email if needed
        if new_email and new_email != old_email:
            user = db.query(models.User).filter(models.User.player_id == player_id).first()
            if user:
                user.email = new_email
                
        db.commit()
        db.refresh(db_player)
    return db_player

def delete_player(db: Session, player_id: UUID):
    db_player = get_player(db, player_id)
    if db_player:
        db_player.status = models.StatusEnum.Cancelled
        
        # Soft delete enrollments
        for enrollment in db_player.enrollments:
            enrollment.status = models.StatusEnum.Cancelled
            
        # Do not delete attendances or transactions to preserve history
        # Optionally, we could disable the user login
        user = db.query(models.User).filter(models.User.player_id == player_id).first()
        if user:
            db.delete(user) # Hard delete the login so they can't log in anymore
            
        db.commit()
    return db_player


# --- Coaches ---

def get_coach(db: Session, coach_id: UUID):
    return db.query(models.Coach).filter(models.Coach.coach_id == coach_id).first()

def get_coaches(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Coach).offset(skip).limit(limit).all()

def create_coach(db: Session, coach: schemas.CoachCreate):
    import auth
    db_coach = models.Coach(**coach.model_dump())
    db.add(db_coach)
    db.commit()
    db.refresh(db_coach)
    
    # Create user account for coach
    if coach.email:
        existing_user = db.query(models.User).filter(models.User.email == coach.email).first()
        if not existing_user:
            user = models.User(
                email=coach.email,
                hashed_password=auth.get_password_hash("coach123"),
                role=models.RoleEnum.Admin
            )
            db.add(user)
            db.commit()
            
    return db_coach


# --- Class Schedules ---

def get_class_schedule(db: Session, class_id: UUID):
    return db.query(models.ClassSchedule).options(joinedload(models.ClassSchedule.coach)).filter(models.ClassSchedule.class_id == class_id).first()

def get_class_schedules(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ClassSchedule).options(joinedload(models.ClassSchedule.coach)).filter(models.ClassSchedule.is_active == True).offset(skip).limit(limit).all()

def create_class_schedule(db: Session, class_schedule: schemas.ClassScheduleCreate):
    db_class = models.ClassSchedule(**class_schedule.model_dump())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

def delete_class_schedule(db: Session, class_id: UUID):
    db_class = get_class_schedule(db, class_id)
    if db_class:
        db_class.is_active = False
        
        # Soft delete enrollments
        for enrollment in db_class.enrollments:
            enrollment.status = models.StatusEnum.Cancelled
            
        db.commit()
    return db_class


# --- Enrollments ---

def create_enrollment(db: Session, enrollment: schemas.EnrollmentCreate):
    db_enrollment = models.Enrollment(**enrollment.model_dump())
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment

def get_enrollments_for_player(db: Session, player_id: UUID):
    return db.query(models.Enrollment).options(joinedload(models.Enrollment.class_schedule)).filter(models.Enrollment.player_id == player_id).all()

def get_enrollment(db: Session, enrollment_id: UUID):
    return db.query(models.Enrollment).filter(models.Enrollment.enrollment_id == enrollment_id).first()

def update_enrollment(db: Session, enrollment_id: UUID, enrollment_update: schemas.EnrollmentUpdate):
    db_enrollment = get_enrollment(db, enrollment_id)
    if db_enrollment:
        for key, value in enrollment_update.model_dump(exclude_unset=True).items():
            setattr(db_enrollment, key, value)
        db.commit()
        db.refresh(db_enrollment)
        
        # Update the overall player status based on their enrollments
        player = get_player(db, db_enrollment.player_id)
        if player:
            active_count = sum(1 for e in player.enrollments if e.status == models.StatusEnum.Active)
            paused_count = sum(1 for e in player.enrollments if e.status == models.StatusEnum.Paused)
            
            if active_count > 0:
                player.status = models.StatusEnum.Active
            elif paused_count > 0:
                player.status = models.StatusEnum.Paused
            else:
                player.status = models.StatusEnum.Inactive
            db.commit()
            
    return db_enrollment

def get_class_roster(db: Session, class_id: UUID):
    enrollments = db.query(models.Enrollment).options(
        joinedload(models.Enrollment.player)
    ).filter(models.Enrollment.class_id == class_id, models.Enrollment.status == models.StatusEnum.Active).all()
    return [e.player for e in enrollments if e.player]


# --- Transactions ---

def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    db_transaction = models.Transaction(**transaction.model_dump())
    db.add(db_transaction)
    
    # Update player balance
    player = get_player(db, transaction.player_id)
    if player:
        if transaction.type == models.TransactionTypeEnum.Credit_Purchase:
            player.current_balance += Decimal(str(transaction.amount))
        elif transaction.type == models.TransactionTypeEnum.Class_Fee_Deduction:
            player.current_balance -= Decimal(str(transaction.amount))
            
            
    db.commit()
    db.refresh(db_transaction)
    return db_transaction
