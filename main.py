from fastapi import FastAPI
from routers import users, classes, attendance, import_data, coaches, auth, transactions, dashboard
import models
from database import engine

# In a real production app, you'd rely purely on Alembic for migrations.
# But for local dev without migrations run yet, this can create tables if they don't exist.
models.Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Sports Academy Management API",
    description="API for managing players, classes, attendance, and billing.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(classes.router)
app.include_router(attendance.router)
app.include_router(import_data.router)
app.include_router(coaches.router)
app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(dashboard.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Sports Academy Management API. Go to /docs for Swagger UI."}
