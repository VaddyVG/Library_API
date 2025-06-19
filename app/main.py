from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import books, reservations
from app.databases.database import engine, Base
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создание таблиц с обработкой ошибок
    try:
        logger.info("Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables created successfully!")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise
    
    yield  # Работа приложения
    
    logger.info("Shutting down...")
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(books.router)
app.include_router(reservations.router)

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Library API"}
