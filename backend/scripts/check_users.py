import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import SessionLocal
from sqlalchemy import text

async def main():
    async with SessionLocal() as db:
        res = await db.execute(text("SELECT id, name, email, avatar_url FROM users"))
        rows = res.all()
        for r in rows:
            print(dict(r._mapping))

if __name__ == '__main__':
    asyncio.run(main())
