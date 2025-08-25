import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
# Get the directory where this file is located
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{os.path.join(APP_DIR, 'data.db')}")

# Create async engine
async_engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "false").lower() == "true",
    pool_pre_ping=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()

async def init_db():
    """Initialize database tables"""
    try:
        print("Creating database tables...")
        async with async_engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Database tables created successfully")
            
            # Verify tables were created using the connection
            def get_table_names(connection):
                from sqlalchemy import inspect
                inspector = inspect(connection)
                return inspector.get_table_names()
            
            tables = await conn.run_sync(get_table_names)
            print(f"📋 Tables created: {tables}")
            
    except Exception as e:
        print(f"❌ Failed to create database tables: {e}")
        raise

async def get_db():
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def close_db():
    """Close database connections"""
    await async_engine.dispose()
