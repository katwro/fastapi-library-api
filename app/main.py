from fastapi import FastAPI

from app.routers import books, auth, authors
from app.routers import loans, users

app = FastAPI()

app.include_router(auth.router)
app.include_router(authors.router)
app.include_router(books.router)
app.include_router(loans.router)
app.include_router(users.router)
