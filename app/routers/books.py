from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import Book, BookCreate
from app.services.book_services import get_book, get_books_by_author, create_book
from app.databases.database import get_db


router = APIRouter(prefix="/books", tags=["Books"])

@router.get("/all_books", 
            response_model=list[Book],
            summary="Получить все книги",
            description="Список всех книг в библиотеке")
async def list_books(db: AsyncSession = Depends(get_db)):
    return await get_books_by_author(db, "")


@router.post("/create_book", 
             response_model=Book, 
             status_code=status.HTTP_201_CREATED,
             summary="Добавить новую книгу",
             response_description="Созданная книга")
async def create_new_book(
    book: BookCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создание новой книги"""
    return await create_book(db, book)


@router.get("/{book_id}", 
            response_model=Book,
            summary="Получить книгу по ID",
            response_description="Найденная книга",
            responses={
                404: {"description": "Книга не найдена"}
            })
async def read_book(book_id: int, db: AsyncSession = Depends(get_db)):
    book = await get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Книга не найдена")
    return book


@router.get("/author/{book_author}",
            response_model=list[Book],
            summary="Получить книгу по автору",
            response_description="Список найденных книг",
            responses={
                404: {"description": "Книги этого автора не найдены"}
            })
async def book_by_author(book_author: str,
                             db: AsyncSession = Depends(get_db)):
    book = await get_books_by_author(db, book_author)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Книги автора '{book_author}' не найдены")
    return book
