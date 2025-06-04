from sqlalchemy import select
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Book
from app.schemas import BookCreate


async def get_book(db: AsyncSession, book_id: int):
    result = await db.execute(select(Book).where(Book.id == book_id))
    return result.scalar_one_or_none()


async def get_books_by_author(db: AsyncSession, author: str):
    result = await db.execute(select(Book).where(Book.author.ilike(f"%{author.strip()}%")))
    return result.scalars().all()


async def create_book(db: AsyncSession, book_data: BookCreate) -> Book:
    """
    Создает новую книгу в базе данных
    Args:
        db: Асинхронная сессия SQLAlchemy
        book_data: Данные книги (Pydantic схема BookCreate)
    Return:
        Созданный объект Book
    """
    try:
        book_dict = book_data.model_dump()  # Преобразуем Pydantic модель в словарь перед распаковкой
        book = Book(**book_dict)
        db.add(book)
        await db.commit()
        await db.refresh(book)
        return book
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании книги: {str(e)}"
        )
