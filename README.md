# Sports Academy API

This is the backend API for the Sports Academy Management System. It powers the frontend UI and handles all business logic, data persistence, and authentication.

## Technologies Used
- **Python 3.11**
- **FastAPI**: High-performance web framework for building APIs.
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) for database interactions.
- **SQLite**: Local file-based database for development.
- **Uvicorn**: ASGI web server implementation.
- **PyJWT & Passlib**: For secure JWT-based authentication and password hashing.

## Key Features & Functionality
- **Authentication**: JWT-based login system supporting multiple roles (Admin, Student, Coach).
- **Player Management**: Create, read, update, and soft-delete players.
- **Class Schedules**: Full CRUD operations for class schedules, including automated fee management.
- **Enrollments & Attendance**: Track which players are enrolled in which classes, and record daily attendance.
- **Wallet & Transactions**: Wallet-based system where players can top-up balances, and class attendance automatically deducts credits.
- **Data Import**: Built-in endpoints to import legacy data from PDFs or CSVs.

## How to Run Locally

1. **Activate the Virtual Environment**:
   ```bash
   source venv/bin/activate
   ```
2. **Install Dependencies** (if needed):
   ```bash
   pip install -r requirements.txt
   ```
3. **Start the Development Server**:
   ```bash
   uvicorn main:app --port 8345 --reload
   ```
   The API will be available at `http://localhost:8345`. 
   *Note: Interactive API documentation is automatically generated and available at `http://localhost:8345/docs`.*

## Default Logins (For Testing)
You can use these credentials to log in to the associated frontend UI:
- **Admin**: `admin@sportsacademy.com` / `admin123`
- **Student**: `player@sportsacademy.com` / `player123`
- **Coach (Admin Access)**: `testCoach@gmail.com` / `coach123`
