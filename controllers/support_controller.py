from fastapi import FastAPI, HTTPException
from config.postgres_config import PostgresDB  # Import your database configuration
import models.users_model as users_model  # Import your Pydantic model
from models import support_model
from utils.PasswordHash import hash_password, verify_password
import datetime
import secrets
import string
from utils import send_mail
from typing import Union
app = FastAPI()

async def create_ticket(ticket_data):
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        query = """
           INSERT INTO tickets(user_id, subject, description,status, created_at, updated_at)
           VALUES ($1, $2, $3, $4, $5, $6)
           RETURNING ticket_id;
           """
        # Current timestamp
        current_time = datetime.datetime.now()
        ticket_data.created_at = current_time
        ticket_data.updated_at = current_time

        ticket_id = await conn.fetchval(query, ticket_data.user_id, ticket_data.subject, ticket_data.description,
                                        ticket_data.status or 'open', ticket_data.created_at, ticket_data.updated_at)

    return {"ticket_id": ticket_id, "message": "Ticket created successfully"}

async def update_ticket(ticket_id: int, ticket_update: support_model.TicketUpdateModel):
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        query_parts = ["UPDATE tickets SET"]
        values = []
        query_index = 1

        if ticket_update.agent_id is not None:
            query_parts.append(f"agent_id = ${query_index},")
            values.append(ticket_update.agent_id)
            query_index += 1

        if ticket_update.status is not None:
            query_parts.append(f"status = ${query_index},")
            values.append(ticket_update.status.value)
            query_index += 1

        # Ensure there is at least one field to update
        if not values:
            raise HTTPException(status_code=400, detail="No fields to update")

        query_parts.append(f"updated_at = ${query_index} WHERE ticket_id = ${query_index + 1} RETURNING *;")
        current_time = datetime.datetime.now()
        values.extend([current_time, ticket_id])

        query = " ".join(query_parts).replace(", WHERE", " WHERE")
        updated_ticket_record = await conn.fetchrow(query, *values)

        if updated_ticket_record is None:
            raise HTTPException(status_code=404, detail="Ticket not found")

        # Convert the record to a dictionary before returning
        updated_ticket_dict = {key: value for key, value in updated_ticket_record.items()}
        return updated_ticket_dict


async def get_all_tickets():
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        query = "SELECT * FROM tickets;"
        tickets_records = await conn.fetch(query)

        # Convert the list of records to a list of dictionaries
        tickets_list = [dict(record) for record in tickets_records]
        return tickets_list


async def get_ticket_status_counts():
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        # First, fetch the counts for each status that is present in the database
        query = """
            SELECT status, COUNT(*) 
            FROM tickets 
            GROUP BY status;
        """
        status_records = await conn.fetch(query)

        # Initialize a dictionary with a count of 0 for each possible status
        status_counts = {status.value: 0 for status in support_model.Status}

        # Update the counts for each status that has records
        for record in status_records:
            status_counts[record['status']] = record['count']

        return status_counts

async def get_tickets_by_user(user_id: str):
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        query = """
            SELECT * FROM tickets 
            WHERE user_id = $1;
        """
        tickets_records = await conn.fetch(query, user_id)

        # Convert the list of records to a list of dictionaries
        tickets_list = [dict(record) for record in tickets_records]
        return tickets_list