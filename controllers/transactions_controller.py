from typing import List
from config.postgres_config import PostgresDB
import models.transactions_model as transactions_model
from fastapi import FastAPI, HTTPException
from decimal import Decimal
async def fetch_transactions_by_user_id(user_id: str):
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        query = "SELECT * FROM transactions WHERE user_id = $1 AND deleted_at IS NULL;"
        rows = await conn.fetch(query, user_id)
        return [transactions_model.Transaction(**dict(row)) for row in rows]

async def fetch_transactions(oversee_id: str, status: str) -> List[transactions_model.Transaction]:
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        if oversee_id.startswith('AU'):
            query = """
                   SELECT t.*, a.email as email
                   FROM transactions AS t 
                   JOIN user_auths AS a ON t.user_id = a.user_id 
                   WHERE t.status = $1 
                   AND t.deleted_at IS NULL;
                   """
            rows = await conn.fetch(query, status)
        else:
            query = """
                   SELECT t.*, a.email 
                   FROM transactions AS t 
                   JOIN user_profiles AS u ON t.user_id = u.user_id 
                   JOIN user_auths AS a ON u.user_id = a.user_id 
                   WHERE u.oversee_user = $1 
                   AND t.status = $2 
                   AND t.deleted_at IS NULL;
                   """
            rows = await conn.fetch(query, oversee_id, status)

        return [transactions_model.Transaction(**dict(row)) for row in rows]

async def update_transaction_status(transaction_id: int, status: str):
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            # Fetch the transaction to update
            transaction = await conn.fetchrow("SELECT * FROM transactions WHERE id = $1", transaction_id)
            if not transaction:
                raise HTTPException(status_code=404, detail="Transaction not found")

            # Update the transaction status
            await conn.execute("UPDATE transactions SET status = $1 WHERE id = $2", status, transaction_id)

            if status == "Approved":
                # Adjust the user's balance if the transaction is approved
                user_id = transaction['user_id']
                amount = float(transaction['amount'])
                is_deposit = transaction['is_deposit']

                user = await conn.fetchrow("SELECT * FROM user_profiles WHERE user_id = $1", user_id)
                if not user:
                    raise HTTPException(status_code=404, detail="User not found")

                current_balance = float(user['balance']) if user['balance'] is not None else 0.0
                new_balance = current_balance + amount if is_deposit else current_balance - amount

                # Update the user's balance
                await conn.execute("UPDATE user_profiles SET balance = $1 WHERE user_id = $2", new_balance, user_id)

            return await conn.fetchrow("SELECT * FROM transactions WHERE id = $1", transaction_id)

async def get_status_counts() -> dict[str, int]:
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        query = """
               SELECT status, COUNT(*) AS count
               FROM transactions 
               WHERE status IN ('Approved', 'Rejected', 'Pending') 
               GROUP BY status;
               """
        rows = await conn.fetch(query)

        # Initialize a dictionary to store the counts
        status_counts = {'Approved': 0, 'Rejected': 0, 'Pending': 0}

        for row in rows:
            status_counts[row['status']] = row['count']

        return status_counts
