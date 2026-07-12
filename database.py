import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from google.cloud.alloydb.connector import Connector, IPTypes

# Retrieve configuration from environment variables
ALLOYDB_INSTANCE = os.getenv(
    "ALLOYDB_INSTANCE",
    "projects/project-861ad996-4f43-41e8-b56/locations/us-central1/clusters/sports-academy-db/instances/primary"
)
DB_USER = os.getenv("DB_USER", "tech.svvclub@gmail.com")
DB_PASS = os.getenv("DB_PASS", "")  # Usually empty for IAM
DB_NAME = os.getenv("DB_NAME", "postgres") # Default database
USE_IAM_AUTH = os.getenv("USE_IAM_AUTH", "true").lower() == "true"

# Initialize Connector object
connector = Connector()

# Function to return the database connection object
def getconn():
    conn = connector.connect(
        ALLOYDB_INSTANCE,
        "pg8000",
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME,
        enable_iam_auth=USE_IAM_AUTH,
        ip_type=IPTypes.PUBLIC,
    )
    return conn

# Create connection pool with 'creator' argument to our connection object function
engine = create_engine(
    "postgresql+pg8000://",
    creator=getconn,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
