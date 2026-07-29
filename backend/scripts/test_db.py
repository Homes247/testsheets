import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import SessionLocal
from sqlalchemy import text

async def main():
    print("Connecting to db...")
    async with SessionLocal() as db:
        result = await db.execute(text("SELECT COUNT(*) FROM documents"))
        count = result.scalar()
        print(f"Found {count} documents.")

if __name__ == '__main__':
    asyncio.run(main())
