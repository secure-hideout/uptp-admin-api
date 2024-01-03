# controllers.py
from config.postgres_config import PostgresDB  # Import your database configuration
import models.user_profile_model as user_profile_model  # Import your Pydantic models
from fastapi import HTTPException
from datetime import datetime
from typing import List
from utils.jwt_verify import verify_token
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends


async def update_user_balance(update_data: user_profile_model.UserBalanceUpdateModel):
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        # Check if user exists and get current balance
        existing_user = await conn.fetchrow("SELECT * FROM user_profiles WHERE user_id = $1", update_data.user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        current_balance = float(existing_user['balance']) if existing_user['balance'] is not None else 0.0

        # Determine if the transaction is a deposit or withdrawal
        is_deposit = update_data.balance >= 0

        # If amount is negative and a withdrawal is intended, check against the current balance
        if not is_deposit and abs(update_data.balance) > current_balance:
            raise HTTPException(status_code=400, detail="Insufficient funds for withdrawal")

        # Determine status based on oversee_id
        status = "Pending" if update_data.oversee_id.startswith("IU") else "Approved"

        # Add record in transactions table
        transaction_query = """
            INSERT INTO transactions (user_id, amount, is_deposit, created_at, updated_at, currency, status)
            VALUES ($1, $2, $3, $4, $4, $5, $6) RETURNING *;
        """
        transaction_record = await conn.fetchrow(
            transaction_query,
            update_data.user_id,
            abs(update_data.balance),  # Use the absolute value of the balance
            is_deposit,
            datetime.now(),
            update_data.currency,
            status
        )

        # If the status is 'Approved', update the balance
        if status == "Approved":
            new_balance = current_balance + (update_data.balance if is_deposit else -abs(update_data.balance))

            # Update the balance in the database
            update_query = "UPDATE user_profiles SET balance = $1 WHERE user_id = $2 RETURNING *;"
            row = await conn.fetchrow(update_query, new_balance, update_data.user_id)
            if not row:
                raise HTTPException(status_code=404, detail="User not found")

            updated_user_profile = user_profile_model.UserProfile(**dict(row))
            return updated_user_profile
        else:
            # If the status is 'Pending', do not update the balance
            return {"message": "Transaction recorded with status 'Pending'"}

async def create_agent_token_mapping(mapping_data: user_profile_model.AgentTokenMappingPayload):
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        try:
            # Start a transaction
            transaction = conn.transaction()
            await transaction.start()

            # Delete existing records not in the new list
            existing_ids = [item.id for item in mapping_data.stocks]
            await conn.execute(
                "DELETE FROM agent_token_mappings WHERE user_id = $1 AND financial_instrument_id != ALL($2)",
                mapping_data.user_id, existing_ids
            )

            # Insert new records
            for stock in mapping_data.stocks:
                await conn.execute(
                    "INSERT INTO agent_token_mappings (user_id, financial_instrument_id, instrument_type) VALUES ($1, $2, $3) ON CONFLICT (user_id, financial_instrument_id, instrument_type) DO NOTHING",
                    mapping_data.user_id, stock.id, stock.instrument_type  # Assuming 'Stock' as instrument_type
                )

            # Commit transaction
            await transaction.commit()
            return {"message": "Record Updated Successfully"}

        except Exception as e:
            await transaction.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
async def get_agent_token_mappings_by_user_id(user_id: str) -> List[user_profile_model.AgentTokenMapping]:

    query = """
        SELECT atm.user_id, atm.financial_instrument_id, atm.instrument_type, zi.tradingsymbol
        FROM agent_token_mappings atm
        LEFT JOIN zinstruments zi ON atm.financial_instrument_id = zi.zid
        WHERE atm.user_id = $1;
    """

    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        try:
            rows = await conn.fetch(query, user_id)
            return [user_profile_model.AgentTokenMapping(**dict(row)) for row in rows]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")