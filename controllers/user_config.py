from fastapi import FastAPI, HTTPException
from collections import defaultdict
from config.postgres_config import PostgresDB  # Import your database configuration
import models.users_model as users_model  # Import your Pydantic model
from utils.PasswordHash import hash_password, verify_password
import datetime
import secrets
import string
from utils import send_mail
from typing import Union
import models.users_model as users_model, models.user_profile_model as user_profile_model, \
    models.trade_model as trades_model, models.transactions_model as transactions_model, models.auth_model as auth_model, models.user_config as user_config
import controllers.user_controller as user_controller, controllers.user_profile_controller as user_profile_controller, \
    controllers.trades_controller as trades_controller, controllers.transactions_controller as transactions_controller, \
    controllers.auth_controller as auth_controller
async def create_users_config(config_data: user_config.UsersConfig):
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        query = """
            INSERT INTO users_config (user_id, type, conf, value) 
            VALUES ($1, $2, $3, $4);
        """
        await conn.execute(query, config_data.user_id, config_data.type, config_data.conf, config_data.value)
        return config_data

async def update_users_config(user_id: str, config_data: user_config.UsersConfig):
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        query = """
            UPDATE users_config SET type = $2, conf = $3, value = $4 
            WHERE user_id = $1;
        """
        await conn.execute(query, user_id, config_data.type, config_data.conf, config_data.value)
        return config_data

async def get_users_config(user_id: str):
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        query = "SELECT * FROM users_config WHERE user_id = $1;"
        rows = await conn.fetch(query, user_id)
        return [user_config.UsersConfig(**dict(row)) for row in rows]

async def create_user_config(request_data: user_config.CreateUserConfigRequest):
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        # Insert user details into user_auths or relevant table here

        # Insert config items into users_config
        for config_type, config_items in request_data.config.items():
            for conf, value in config_items.dict().items():
                if value is not None:
                    query = """
                        INSERT INTO users_config (user_id, type, conf, value)
                        VALUES ($1, $2, $3, $4);
                    """
                    await conn.execute(query, request_data.user_id, config_type, conf, value)

        return {"message": "User and configurations created successfully"}


async def get_user_config(user_id: str) -> user_config.UserConfigResponse:
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        query = "SELECT type, conf, value FROM users_config WHERE user_id = $1;"
        rows = await conn.fetch(query, user_id)

        if not rows:
            raise HTTPException(status_code=404, detail="User configuration not found")

        # Organize data into the desired structure
        config_data = defaultdict(lambda: defaultdict(str))
        for row in rows:
            config_data[row['type']][row['conf']] = row['value']

        return user_config.UserConfigResponse(user_id=user_id, config=dict(config_data))

async def upsert_user_config(request_data: user_config.UserConfigRequest):
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        # Loop through each config type (e.g., "NSE", "Crypto") and their settings
        for config_type, config_items in request_data.config.items():
            for conf, value in config_items.dict().items():
                if value is not None:
                    # Perform upsert for each configuration item
                    query = """
                        INSERT INTO users_config (user_id, type, conf, value)
                        VALUES ($1, $2, $3, $4)
                        ON CONFLICT (user_id, type, conf)
                        DO UPDATE SET value = EXCLUDED.value;
                    """
                    await conn.execute(query, request_data.user_id, config_type, conf, value)

        return {"message": "User configurations updated successfully"}