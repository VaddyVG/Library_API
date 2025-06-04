from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from app.models import Book, Reservation as ReservationModel
from app.schemas import ReservationCreate, Reservation as ReservationSchema
from app.databases.database import get_db
from app.services.penalty_services import calculate_penalty


router = APIRouter(prefix="/reservations", tags=['Reservations'])

@router.post("/", response_model=ReservationSchema,
             status_code=status.HTTP_201_CREATED,
             summary="Создать новое бронирование",
             responses={
                 400: {"description": "Книга доступна для бронирования"},
                 404: {"description": "Книга не найдена"}
             })
async def create_reservation(
    reservation: ReservationCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Создает новое бронирование книги.
    
    Параметры:
    - book_id: ID книги (обязательно)
    - user_id: ID пользователя (обязательно)
    - days: срок бронирования в днях (обязательно, мин 1, макс 30)
    """
    async with db.begin():
        book = await db.get(Book, reservation.book_id, with_for_update=True)

        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Книга не найдена"
            )
        
        if not book.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Книга недоступна"
            )
        
        # Обновление статуса книги
        book.is_available = False
        await db.flush()

        # Создаем бронирование
        db_reservation = ReservationModel(
            book_id = reservation.book_id,
            user_id = reservation.user_id,
            expires_at = datetime.now() + timedelta(days=reservation.days)
        )

        db.add(db_reservation)
        db.commit()
        db.refresh(db_reservation)

    return db_reservation


@router.get("/{book_id}/penalty")
async def get_penalty(book_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ReservationModel).
        where(ReservationModel.book_id == book_id, ReservationModel.is_returned == False)
    )
    reservation = result.scalar_one_or_none()
    return {"penalty": calculate_penalty(reservation.expires_at) if reservation else 0}


@router.post(
    "/{reservation_id}/return",
    response_model=ReservationSchema,
    summary="Вернуть книгу",
    responses={
        404: {"description": "Бронирование не найдено"},
        400: {"description": "Книга уже возращена"}
    }
)
async def return_book(
    reservation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Отмечает книгу как возвращенную и обновляет ее статус доступности.
    """
    async with db.begin():
        # Находим бронирование
        reservation = await db.get(ReservationModel, reservation_id, with_for_update=True)

        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Бронирование не найдено"
            )
        
        if reservation.is_returned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Книга уже возращена"
            )

        # Обновляем статус книги
        book = await db.get(Book, reservation.book_id)
        book.is_available = True

        # Обновляем бронирование
        reservation.is_returned = True
        reservation.reserved_at = datetime.now()

    return reservation
