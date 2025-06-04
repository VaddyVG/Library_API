from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


try:
    engine = create_async_engine(settings.DB_URL, echo=True)
    logger.info(f"Database engine created for {settings.DB_URL}")
except Exception as e:
    logger.error(f"Error creating engine: {e}")
    raise


AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
