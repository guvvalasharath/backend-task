import asyncio
from app.db.base import engine, Base
from app.db import models

async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_all())
    print("Tables created.")
