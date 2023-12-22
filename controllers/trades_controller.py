from typing import List
from config.postgres_config import PostgresDB
import models.trade_model as trades_model
from fastapi import HTTPException
async def fetch_trades_by_user_id(user_id: str) -> List[trades_model.Trade]:
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        query = "SELECT * FROM trades WHERE user_id = $1 AND deleted_at IS NULL;"
        rows = await conn.fetch(query, user_id)
        return [trades_model.Trade(**dict(row)) for row in rows]

async def get_all_zinstruments() -> List[trades_model.ZInstrument]:
    query = "SELECT * FROM zinstruments;"

    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch(query)
            return [trades_model.ZInstrument(**dict(row)) for row in rows]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")