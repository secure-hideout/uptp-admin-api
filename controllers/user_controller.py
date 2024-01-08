from fastapi import FastAPI, HTTPException
from config.postgres_config import PostgresDB  # Import your database configuration
import models.users_model as users_model  # Import your Pydantic model
from utils.PasswordHash import hash_password, verify_password
import datetime
import secrets
import string
from utils import send_mail
from typing import Union
app = FastAPI()


async def read_users_by_oversee_user(oversee_user_id: Union[str, None]=None):
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        if oversee_user_id:
            # Fetch users where oversee_user in user_profiles matches the provided user_id
            query = """
                SELECT ua.* FROM user_auths ua
                JOIN user_profiles up ON ua.user_id = up.user_id
                WHERE up.oversee_user = $1;
            """
            rows = await conn.fetch(query, oversee_user_id)
        else:
            # Fetch all users
            query = "SELECT * FROM user_auths WHERE user_id LIKE 'IU%'"
            rows = await conn.fetch(query)

        return [users_model.UserGet(**dict(row)) for row in rows]


async def read_users():
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:  # Use context manager for connection handling
        try:
            query = "SELECT * FROM user_auths WHERE user_role = 'IU';"
            rows = await conn.fetch(query)
            users = [users_model.UserGet(**dict(row)) for row in rows]
            return users
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

async def read_users_by_role(role):
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:  # Use context manager for connection handling
        try:
            query = "SELECT * FROM user_auths WHERE user_role = $1;"
            rows = await conn.fetch(query, role)
            users = [users_model.UserGet(**dict(row)) for row in rows]
            return users
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

async def generate_unique_user_id(role_prefix, conn):
    while True:
        random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        user_id = f"{role_prefix}-{random_part}"
        if not await conn.fetchrow("SELECT * FROM user_auths WHERE user_id = $1", user_id):
            return user_id

async def create_user(user_data):  # Type the parameter with your Pydantic model
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        email = user_data.email.lower()
        existing_user = await conn.fetchrow("SELECT * FROM user_auths WHERE email = $1", email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email Already exists")

        # Generate a random password
        password_characters = string.ascii_letters + string.digits
        random_password = ''.join(secrets.choice(password_characters) for i in range(10))
        hashed_password = hash_password(random_password)
        print(random_password)
        send_mail.send_email(
            subject="Hola! "+user_data.first_name+" "+user_data.last_name,
            password=random_password,
            email=email,
            to_email=email,
            from_email="connect@uptp.com",
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            smtp_user="hideoutprotocol@gmail.com",
            smtp_password="bdbp opkn heyw ypaa",
            template_name="otp.html",
            name=user_data.first_name+" "+user_data.last_name
        )
        # Generate a unique user_id
        role_prefix = user_data.user_role[:3].upper()  # Assuming the role prefix is the first 3 characters of the role
        user_id = await generate_unique_user_id(role_prefix, conn)

        # Current timestamp
        current_time = datetime.datetime.now()

        # Insert into user_auths table
        user_auth_query = """
            INSERT INTO user_auths (user_id, created_at, updated_at, email, password, user_role, first_name, last_name, is_active)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING *;
        """
        await conn.fetchrow(user_auth_query, user_id, current_time, current_time,
                            email, hashed_password, user_data.user_role,
                            user_data.first_name, user_data.last_name, 'true')

        # Insert into user_profiles table
        user_profile_query = """
            INSERT INTO user_profiles (user_id, created_at, updated_at, first_name, last_name, is_enabled, oversee_user)
            VALUES ($1, $2, $3, $4, $5, $6, $7);
        """
        await conn.execute(user_profile_query, user_id, current_time, current_time,
                           user_data.first_name, user_data.last_name, True, user_data.oversee_user)
        print(user_data)
        return {"message": "User created successfully", "user_id": user_id}

async def update_user(update_data):
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            # Update user_auths table
            update_auth_fields = {k: v for k, v in update_data.dict().items() if v is not None and k in {'email', 'first_name', 'last_name', 'user_role'}}
            if update_auth_fields:
                update_auth_query = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_auth_fields.keys())])
                auth_query = f"UPDATE user_auths SET {update_auth_query}, updated_at = $1 WHERE user_id = $2 RETURNING *;"
                auth_values = [datetime.datetime.now(), update_data.user_id] + list(update_auth_fields.values())
                updated_auth = await conn.fetchrow(auth_query, *auth_values)
                if not updated_auth:
                    raise HTTPException(status_code=404, detail="User not found in auths")

            # Assuming you want to update first_name and last_name in user_profiles table
            update_profile_fields = {k: v for k, v in update_data.dict().items() if v is not None and k in {'first_name', 'last_name'}}
            if update_profile_fields:
                update_profile_query = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(update_profile_fields.keys())])
                profile_query = f"UPDATE user_profiles SET {update_profile_query}, updated_at = $1 WHERE user_id = $2 RETURNING *;"
                profile_values = [datetime.datetime.now(), update_data.user_id] + list(update_profile_fields.values())
                updated_profile = await conn.fetchrow(profile_query, *profile_values)
                if not updated_profile:
                    raise HTTPException(status_code=404, detail="User not found in profiles")

            # Update users_config table
            if 'config' in update_data.dict():
                await conn.execute("DELETE FROM users_config WHERE user_id = $1", update_data.user_id)
                config_insert_query = "INSERT INTO users_config(user_id, type, conf, value) VALUES ($1, $2, $3, $4)"
                for config_type, configs in update_data.config.items():
                    for conf_key, conf_value in configs.items():
                        await conn.execute(config_insert_query, update_data.user_id, config_type, conf_key, conf_value)

            return {
                "user_id": update_data.user_id,
                "updated_auth": dict(updated_auth) if 'updated_auth' in locals() else {},
                "updated_profile": dict(updated_profile) if 'updated_profile' in locals() else {},
                "message": "User updated successfully"
            }

async def delete_user(delete_data: users_model.UserDeleteModel):
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        # Check if user exists
        existing_user = await conn.fetchrow("SELECT * FROM user_auths WHERE user_id = $1", delete_data.user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        print(existing_user)
        # Set deleted_at to the current time
        current_time = datetime.datetime.now()

        # Perform the deletion (setting deleted_at)
        query = "UPDATE user_auths SET deleted_at = $1, is_active = 'false' WHERE user_id = $2 RETURNING *;"
        values = [current_time, delete_data.user_id]

        row = await conn.fetchrow(query, *values)

        if not row:
            raise HTTPException(status_code=404, detail="User not found")

        updated_user = users_model.UserGet(**dict(row))  # Assuming UserGet is your Pydantic model for user retrieval
        return updated_user

async def fetch_users_by_filter(user_role: str, is_active: str):
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        # Building the WHERE clause based on filters
        conditions = ["user_auths.user_id = user_profiles.user_id"]
        if user_role:
            conditions.append(f"user_auths.user_role = '{user_role}'")
        if is_active:
            conditions.append(f"user_auths.is_active = '{is_active}'")
        conditions.append("user_auths.deleted_at IS NULL")

        where_clause = ' AND '.join(conditions) if conditions else '1=1'

        # Adjust the query to join with user_profiles table
        query = f"""
            SELECT user_auths.*, user_profiles.balance
            FROM user_auths
            INNER JOIN user_profiles ON user_auths.user_id = user_profiles.user_id
            WHERE {where_clause};
        """
        rows = await conn.fetch(query)
        return [users_model.UserGet(**dict(row)) for row in rows]

async def api_get_user_counts(oversee_user_id: Union[str,None] = None):
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        # Building the WHERE clause based on the presence of oversee_user_id
        conditions = ["user_auths.deleted_at IS NULL", "user_auths.user_role = 'IU'"]
        params = []

        if oversee_user_id:
            conditions.append("user_profiles.oversee_user = $1")
            params.append(oversee_user_id)

        where_clause = ' AND '.join(conditions)

        query = f"""
                SELECT
                    SUM(CASE WHEN user_auths.is_active = 'true' THEN 1 ELSE 0 END) AS active_count,
                    SUM(CASE WHEN user_auths.is_active = 'false' THEN 1 ELSE 0 END) AS inactive_count
                FROM user_auths
                LEFT JOIN user_profiles ON user_auths.user_id = user_profiles.user_id
                WHERE {where_clause};
            """

        row = await conn.fetchrow(query, *params)
        return {"active_count": row['active_count'], "inactive_count": row['inactive_count']}


async def api_get_agent_counts():
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        query = """
                SELECT
                    SUM(CASE WHEN is_active = 'true' AND deleted_at IS NULL AND user_role = 'AG' THEN 1 ELSE 0 END) AS active_count,
                    SUM(CASE WHEN is_active = 'false' AND deleted_at IS NULL AND user_role = 'AG' THEN 1 ELSE 0 END) AS inactive_count
                FROM user_auths;
            """

        row = await conn.fetchrow(query)
        return {"active_count": row['active_count'], "inactive_count": row['inactive_count']}

async def forgot_password(request_data: users_model.ForgotPasswordRequest):
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        user_email = request_data.email.lower()
        existing_user = await conn.fetchrow("SELECT * FROM user_auths WHERE email = $1", user_email)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Generate a new random password
        new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
        hashed_password = hash_password(new_password)

        # Update the user's password in the database
        await conn.execute(
            "UPDATE user_auths SET password = $1 WHERE email = $2",
            hashed_password, user_email
        )

        # Send an email with the new password
        try:
            send_mail.send_email(
                subject="UPTP Password Reset",
                to_email=user_email,
                from_email="connect@uptp.com",
                smtp_server="smtp.gmail.com",
                smtp_port=587,
                smtp_user="hideoutprotocol@gmail.com",
                smtp_password="bdbp opkn heyw ypaa",
                template_name="password_reset.html",
                password=new_password  # Include other required parameters for your email template
            )
            return {"message": "A new password has been sent to your email"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

async def update_password(request_data: users_model.UpdatePasswordRequest):
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        user_email = request_data.email.lower()
        existing_user = await conn.fetchrow("SELECT * FROM user_auths WHERE email = $1", user_email)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Verify the current password
        if not verify_password(existing_user['password'], request_data.current_password):
            raise HTTPException(status_code=403, detail="Current password is incorrect")

        # Hash the new password
        hashed_new_password = hash_password(request_data.new_password)

        # Update the password in the database
        await conn.execute(
            "UPDATE user_auths SET password = $1 WHERE email = $2",
            hashed_new_password, user_email
        )

        return {"message": "Password updated successfully"}

async def update_password_userid(request_data: users_model.UpdatePasswordRequestUserId):
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        user_id = request_data.userId
        existing_user = await conn.fetchrow("SELECT * FROM user_auths WHERE user_id = $1", user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Verify the current password
        if not verify_password(existing_user['password'], request_data.current_password):
            raise HTTPException(status_code=403, detail="Current password is incorrect")

        # Hash the new password
        hashed_new_password = hash_password(request_data.new_password)

        # Update the password in the database
        await conn.execute(
            "UPDATE user_auths SET password = $1 WHERE user_id = $2",
            hashed_new_password, user_id
        )

        return {"message": "Password updated successfully"}

