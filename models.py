import uuid
import enum
from sqlalchemy import Column, String, Integer, Date, Time, Numeric, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from database import Base
from sqlalchemy import Boolean


class GenderEnum(str, enum.Enum):
    Male = "Male"
    Female = "Female"
    Coed = "Coed"

class RoleEnum(str, enum.Enum):
    Admin = "Admin"
    Student = "Student"

class SkillLevelEnum(str, enum.Enum):
    Beginner = "Beginner"
    Intermediate = "Intermediate"
    Advanced = "Advanced"

class StatusEnum(str, enum.Enum):
    Active = "Active"
    Paused = "Paused"
    Inactive = "Inactive"
    Completed = "Completed"
    Cancelled = "Cancelled"

class AttendanceStatusEnum(str, enum.Enum):
    Attended = "Attended"
    Missed = "Missed"
    Makeup = "Makeup"
    Cancelled = "Cancelled"
    Trial = "Trial"
    Free = "Free"
    Paused = "Paused"

class TransactionTypeEnum(str, enum.Enum):
    Credit_Purchase = "Credit_Purchase"
    Class_Fee_Deduction = "Class_Fee_Deduction"
    Refund = "Refund"
    Adjustment = "Adjustment"

class PaymentMethodEnum(str, enum.Enum):
    Cash = "Cash"
    Card = "Card"
    Bank_Transfer = "Bank_Transfer"
    Credit_Deduct = "Credit_Deduct"

class DayOfWeekEnum(str, enum.Enum):
    Monday = "Monday"
    Tuesday = "Tuesday"
    Wednesday = "Wednesday"
    Thursday = "Thursday"
    Friday = "Friday"
    Saturday = "Saturday"
    Sunday = "Sunday"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(RoleEnum), default=RoleEnum.Student)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.player_id"), nullable=True)

    player = relationship("Player", backref="user")

class Player(Base):
    __tablename__ = "players"

    player_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    parent_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    parent_phone = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(SQLEnum(GenderEnum), nullable=True)
    skill_level = Column(SQLEnum(SkillLevelEnum), nullable=True)
    status = Column(SQLEnum(StatusEnum), default=StatusEnum.Active)
    current_balance = Column(Numeric, default=0.00)
    available_credits = Column(Integer, default=0)
    channel = Column(String, nullable=True)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    enrollments = relationship("Enrollment", back_populates="player")
    attendances = relationship("Attendance", back_populates="player")
    transactions = relationship("Transaction", back_populates="player")

    @property
    def classes(self):
        return [e.class_schedule.class_name for e in self.enrollments if e.class_schedule]

    @property
    def attendance_summary(self):
        total = len(self.attendances)
        attended = sum(1 for a in self.attendances if a.status == AttendanceStatusEnum.Attended)
        if total == 0:
            return "No records"
        return f"{attended}/{total} Attended"


class Coach(Base):
    __tablename__ = "coaches"

    coach_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    specialty = Column(String, nullable=True)

    classes = relationship("ClassSchedule", back_populates="coach")


class ClassSchedule(Base):
    __tablename__ = "class_schedules"

    class_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_name = Column(String, nullable=False)
    target_ages = Column(String, nullable=True)
    coach_id = Column(UUID(as_uuid=True), ForeignKey("coaches.coach_id"), nullable=True)
    location = Column(String, nullable=True)
    capacity = Column(Integer, default=0)
    day_of_week = Column(SQLEnum(DayOfWeekEnum), nullable=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    fee_per_class = Column(Numeric, default=0.00)
    is_active = Column(Boolean, default=True)

    coach = relationship("Coach", back_populates="classes")
    enrollments = relationship("Enrollment", back_populates="class_schedule")
    attendances = relationship("Attendance", back_populates="class_schedule")

class Enrollment(Base):
    __tablename__ = "enrollments"

    enrollment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.player_id"), nullable=False)
    class_id = Column(UUID(as_uuid=True), ForeignKey("class_schedules.class_id"), nullable=False)
    status = Column(SQLEnum(StatusEnum), default=StatusEnum.Active)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)

    player = relationship("Player", back_populates="enrollments")
    class_schedule = relationship("ClassSchedule", back_populates="enrollments")

class Attendance(Base):
    __tablename__ = "attendances"

    attendance_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.player_id"), nullable=False)
    class_id = Column(UUID(as_uuid=True), ForeignKey("class_schedules.class_id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(SQLEnum(AttendanceStatusEnum), nullable=False)

    player = relationship("Player", back_populates="attendances")
    class_schedule = relationship("ClassSchedule", back_populates="attendances")

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.player_id"), nullable=False)
    amount = Column(Numeric, nullable=False)
    type = Column(SQLEnum(TransactionTypeEnum), nullable=False)
    payment_method = Column(SQLEnum(PaymentMethodEnum), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    player = relationship("Player", back_populates="transactions")
