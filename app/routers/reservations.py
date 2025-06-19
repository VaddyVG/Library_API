from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import ReservationCreate, Reservation as ReservationSchema
from app.databases.database import get_db
import app.services.reservations_services as reservation_crud


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
    return await reservation_crud.create_reservation(reservation, db)


@router.get("/{book_id}/penalty")
async def get_penalty(book_id: int, db: AsyncSession = Depends(get_db)):
    return await reservation_crud.penalty(book_id, db)


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
    return await reservation_crud.return_book(reservation_id, db)
