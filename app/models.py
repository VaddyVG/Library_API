from app.databases.database import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    author = Column(String(50), nullable=False)
    genre = Column(String(30))
    is_available = Column(Boolean, default=True)

    # Отношение "один ко многим" с Reservation
    reservations = relationship("Reservation", back_populates="book")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(50))

    # Отношение "один ко многим" с Reservation
    reservations = relationship("Reservation", back_populates="user")

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    reserved_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime)
    is_returned = Column(Boolean, default=False)

    # Отношения "многие к одному"
    book = relationship("Book", back_populates="reservations")
    user = relationship("User", back_populates="reservations")