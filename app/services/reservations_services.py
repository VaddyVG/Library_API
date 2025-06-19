from sqlalchemy import select
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Book, Reservation as ReservationModel
from app.services.penalty_services import calculate_penalty
from app.schemas import ReservationCreate
from app.models import User


async def create_reservation(reservation: ReservationCreate,
                             db: AsyncSession) -> ReservationModel:
    """Получение штрафа
    Args:
        reservation: Pydantic схема ReservationCreate
        db: Сессия AsyncSession
    Return:
        Модель Reservation."""
    async with db.begin():
        book = await db.get(Book, reservation.book_id, with_for_update=True)  # Поиск книги по ID
        user = await db.get(User, reservation.user_id, with_for_update=True)  # Поиск пользователя по ID

        # Проверка существования книги
        if not book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Книга не найдена"
            )

        # Проверка доступности книги
        if not book.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Книга недоступна"
            )

        # Проверка существования пользователя
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователя с таким ID не существует"
            )
        
        book.is_available = False  # Меняем статус книги на недоступна
        await db.flush()  # Обновляем базу данных

        db_reservation = ReservationModel(
            book_id = reservation.book_id,
            user_id = reservation.user_id,
            expires_at = datetime.now() + timedelta(days=reservation.days)
        )  # Обновление бронирования

        db.add(db_reservation)
        db.commit()
        db.refresh(db_reservation)
    return db_reservation


async def penalty(book_id: int, db: AsyncSession):
    """Получение штрафа
    Args:
        book_id: int, id Книги
        db: Сессия AsyncSession
    Return:
        Сумма штрафа или 0."""
    result = await db.execute(
        select(ReservationModel)
        .where(ReservationModel.book_id == book_id, ReservationModel.is_returned == False)
    )
    reservation = result.scalar_one_or_none()
    return {"Штраф":calculate_penalty(reservation.expires_at) if reservation else 0}


async def return_book(reservation_id: int, db: AsyncSession) -> ReservationModel:
    async with db.begin():
        reservation = await db.get(ReservationModel, reservation_id, with_for_update=True)  # Поиск бронирования по ID

        # Проверка существования бронирования
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Бронирование не найдено"
            )

        # Проверка возврата книги
        if reservation.is_returned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Книга уже возвращена"
            )
        
        book = await db.get(Book, reservation.book_id)  # Получение ID книги
        book.is_available = True  # Меняем статус is_available на True в таблице books

        reservation.is_returned = True  # Меняем статус is_returned на True в таблице reservations

    return reservation
