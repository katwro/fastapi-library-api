from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Table
from app.database import Base
from datetime import datetime, timezone


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="USER")

    loans = relationship("Loan", back_populates="user")


book_author = Table(
    "book_author",
    Base.metadata,
    Column("book_id", ForeignKey("books.id"), primary_key=True),
    Column("author_id", ForeignKey("authors.id"), primary_key=True)
)


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    isbn = Column(String, unique=True, index=True, nullable=True)
    available = Column(Boolean, default=True)

    authors = relationship(
        "Author",
        secondary=book_author,
        back_populates="books"
    )

    loans = relationship("Loan", back_populates="book")


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    books = relationship(
        "Book",
        secondary=book_author,
        back_populates="authors"
    )


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), index=True, nullable=False)

    loan_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    due_date = Column(DateTime)
    return_date = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="loans")
    book = relationship("Book", back_populates="loans")
