import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base, get_db
from main import app
import models
import auth

# Setup an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

@pytest.fixture()
def db_session():
    # Create the tables in the test database
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop the tables after the test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    # Clear overrides after the test
    app.dependency_overrides.clear()

@pytest.fixture
def mock_admin_token(client):
    access_token = auth.create_access_token(data={"sub": "admin@test.com", "role": "Admin"})
    return access_token

@pytest.fixture
def test_player(db_session):
    player = models.Player(
        first_name="Test",
        last_name="Player",
        parent_name="Parent Test",
        email="test_player@test.com",
        age=10,
        gender="Male",
        status=models.StatusEnum.Active
    )
    db_session.add(player)
    db_session.commit()
    db_session.refresh(player)

    # create a user for this player
    user = models.User(
        email="test_player@test.com",
        hashed_password=auth.get_password_hash("password"),
        role=models.RoleEnum.Student,
        player_id=player.player_id
    )
    db_session.add(user)
    db_session.commit()
    
    return player

@pytest.fixture
def test_class(db_session):
    cls = models.ClassSchedule(
        class_name="Test Class",
        target_ages="10-12",
        capacity=10,
        day_of_week="Monday",
        fee_per_class=10.0
    )
    db_session.add(cls)
    db_session.commit()
    db_session.refresh(cls)
    return cls

@pytest.fixture
def mock_student_token(test_player):
    access_token = auth.create_access_token(data={
        "sub": test_player.email, 
        "role": "Student",
        "player_id": str(test_player.player_id)
    })
    return access_token
