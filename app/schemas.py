from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class BookBase(BaseModel):
    title: str
    author: str
    genre: Optional[str] = None


class BookCreate(BookBase):
    title: str = Field(..., min_length=1, 
                       max_length=100, 
                       example="Преступление и наказание")
    
    author: str = Field(..., min_length=2, 
                        max_length=50, 
                        example="Фёдор Достоевский")
    
    genre: Optional[str] = Field(None, 
                              max_length=30, 
                              example="Роман")


class Book(BookBase):
    id: int
    is_available: bool

    class Config:
        from_attributes = True


class ReservationBase(BaseModel):
    book_id: int
    user_id: int


class ReservationCreate(ReservationBase):
    days: int = Field(gt=0, le=365, 
                      description="Срок бронирования в днях")


class Reservation(ReservationBase):
    id: int
    reserved_at: datetime
    expires_at: datetime
    is_returned: bool

    class Config:
        from_attributes = True
