# Library Management API

Backend REST API for managing books, authors, and user loans in a library system.

## Setup & Run

### 1. Install dependencies
```
pip install -r requirements.txt
```

### 2. Configure database

Update the connection string in `database.py`:
```
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://user:password@localhost:3306/library"
```
### 3. Initialize database

Run the `library.sql` script to create tables in MySQL.


### 4. Run the application
```
uvicorn app.main:app --reload
```
## API Documentation

Available at: http://localhost:8000/docs

## Authentication
 - Obtain token: `POST /auth/token`
 - Use token in requests:

 Authorization: Bearer <your_token>