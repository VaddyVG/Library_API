from sqlalchemy import select
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Book, Reservation as ReservationModel
from app.services.penalty_services import calculate_penalty
from app.schemas import ReservationCreate


async def create_reservation(reservation: ReservationCreate,
                             db: AsyncSession):
    async with db.begin():
        book = await db.get(Book, reservation.book_id, with_for_update=True)

        if not book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Книга не найдена"
            )
        if not book.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Книга недоступна"
            )
        
        book.is_available = False
        await db.flush()

        db_reservation = ReservationModel(
            book_id = reservation.book_id,
            user_id = reservation.user_id,
            expires_at = datetime.now() + timedelta(days=reservation.days)
        )

        db.add(db_reservation)
        db.commit()
        db.refresh(db_reservation)
    return db_reservation


async def penalty(book_id: int, db: AsyncSession):
    result = await db.execute(
        select(ReservationModel)
        .where(ReservationModel.book_id == book_id, ReservationModel.is_returned == False)
    )
    reservation = result.scalar_one_or_none()
    return {"Штраф":calculate_penalty(reservation.expires_at) if reservation else 0}


async def return_book(reservation_id: int, db: AsyncSession):
    async with db.begin():
        reservation = await db.get(ReservationModel, reservation_id, with_for_update=True)

        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Бронирование не найдено"
            )

        if reservation.is_returned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Книга уже возвращена"
            )
        
        book = await db.get(Book, reservation.book_id)
        book.is_available = True

        reservation.is_returned = True
        reservation.reserved_at = datetime.now()

    return reservation
