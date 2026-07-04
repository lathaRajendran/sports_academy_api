from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, time, datetime
from uuid import UUID

from models import GenderEnum, SkillLevelEnum, StatusEnum, AttendanceStatusEnum, TransactionTypeEnum, PaymentMethodEnum, DayOfWeekEnum

# --- Player Schemas ---

class PlayerBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    parent_name: str
    email: Optional[str] = None
    parent_phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[GenderEnum] = None
    skill_level: Optional[SkillLevelEnum] = None
    status: StatusEnum = StatusEnum.Active
    channel: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    available_credits: int = 0

class PlayerCreate(PlayerBase):
    pass

class PlayerRegister(PlayerBase):
    email: str
    class_id: UUID
    initial_payment: float
    payment_method: PaymentMethodEnum = PaymentMethodEnum.Cash

class PlayerUpdate(PlayerBase):
    pass

class Player(PlayerBase):
    player_id: UUID
    current_balance: float
    classes: Optional[List[str]] = []
    attendance_summary: Optional[str] = None

    class Config:
        from_attributes = True


# --- Coach Schemas ---

class CoachBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    specialty: Optional[str] = None

class CoachCreate(CoachBase):
    pass

class CoachUpdate(CoachBase):
    pass

class Coach(CoachBase):
    coach_id: UUID

    class Config:
        from_attributes = True


# --- ClassSchedule Schemas ---

class ClassScheduleBase(BaseModel):
    class_name: str
    target_ages: Optional[str] = None
    coach_id: Optional[UUID] = None
    location: Optional[str] = None
    capacity: int = 0
    day_of_week: Optional[DayOfWeekEnum] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    fee_per_class: float = 0.00

class ClassScheduleCreate(ClassScheduleBase):
    pass

class ClassSchedule(ClassScheduleBase):
    class_id: UUID
    coach: Optional[Coach] = None

    class Config:
        from_attributes = True

# --- User Schemas ---

from models import RoleEnum

class UserCreate(BaseModel):
    email: str
    password: str
    role: Optional[RoleEnum] = RoleEnum.Student
    player_id: Optional[UUID] = None

class UserResponse(BaseModel):
    id: UUID
    email: str
    role: RoleEnum
    player_id: Optional[UUID] = None

    class Config:
        from_attributes = True


# --- Enrollment Schemas ---

class EnrollmentBase(BaseModel):
    player_id: UUID
    class_id: UUID
    status: StatusEnum = StatusEnum.Active
    start_date: date
    end_date: Optional[date] = None

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentUpdate(BaseModel):
    status: Optional[StatusEnum] = None
    class_id: Optional[UUID] = None

class Enrollment(EnrollmentBase):
    enrollment_id: UUID

    class Config:
        from_attributes = True

class EnrollmentWithClass(Enrollment):
    class_schedule: Optional[ClassSchedule] = None


# --- Attendance Schemas ---

class AttendanceBase(BaseModel):
    player_id: UUID
    class_id: UUID
    date: date
    status: AttendanceStatusEnum

class AttendanceCreate(AttendanceBase):
    pass

class Attendance(AttendanceBase):
    attendance_id: UUID

    class Config:
        from_attributes = True


# --- Transaction Schemas ---

class TransactionBase(BaseModel):
    player_id: UUID
    amount: float
    type: TransactionTypeEnum
    payment_method: PaymentMethodEnum

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    transaction_id: UUID
    timestamp: datetime

    class Config:
        from_attributes = True
