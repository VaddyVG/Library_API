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
    book_dict = book_data.model_dump()  # Преобразуем Pydantic модель в словарь перед распаковкой
    book = Book(**book_dict)

    # Ошибка если книга этого автора с таким же названием уже присутствует
    existing_book = await db.execute(select(Book).filter(Book.title == book.title, Book.author == book.author))
    if existing_book.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Книга этого автора с таким название уже существует"
        )
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book


async def delete_book(book_id: int, db: AsyncSession):
    """Удаление книги по ID
    Args:
        book_id: ID книги, которую нужно удалить
        db: Асинхронная сессия SQLAlchemy
    Return:
        Сообещние об успешном удалении или ошибку 404."""
    book = await db.execute(select(Book).where(Book.id == book_id))
    db_item = book.scalar_one_or_none()

    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Книга не найдена"
        )
    
    await db.delete(db_item)
    await db.commit()
    return {"message": "Книга была удалена"}
    