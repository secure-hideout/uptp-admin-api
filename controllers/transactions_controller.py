from typing import List
from config.postgres_config import PostgresDB
import models.transactions_model as transactions_model

async def fetch_transactions_by_user_id(user_id: str) -> List[transactions_model.Transaction]:
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        query = "SELECT * FROM transactions WHERE user_id = $1 AND deleted_at IS NULL;"
        rows = await conn.fetch(query, user_id)
        return [transactions_model.Transaction(**dict(row)) for row in rows]