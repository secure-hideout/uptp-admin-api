from typing import List, Optional
from config.postgres_config import PostgresDB
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
import models.auth_model as auth_model
from datetime import date
from utils.PasswordHash import verify_password
from utils.generate_jwt_token import create_access_token
import models.users_model as users_model
async def get_login_trackers_by_user_and_date(user_id: str, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[auth_model.LoginTracker]:
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        # Building the WHERE clause based on the provided parameters
        conditions = ["user_id = $1"]
        params = [user_id]

        if start_date:
            conditions.append("created_at::date >= $2")
            params.append(start_date)
        if end_date:
            conditions.append("created_at::date <= $3")
            params.append(end_date)

        where_clause = " AND ".join(conditions)
        query = f"SELECT * FROM login_trackers WHERE {where_clause};"

        print(query, params)
        rows = await conn.fetch(query, *params)
        if not rows:
            raise HTTPException(status_code=404, detail="No records found")

        return [auth_model.LoginTracker(**dict(row)) for row in rows]

async def login_for_access_token(form_data: auth_model.LoginRequest):
    pool = await PostgresDB.get_pool()
    async with pool.acquire() as conn:
        try:
            # Query to fetch user by email
            query = "SELECT * FROM user_auths WHERE email = $1;"
            row = await conn.fetchrow(query, form_data.email.lower())
            print(form_data.password, row.get('password'))
            if row is None or not verify_password(row.get('password'), form_data.password):
                # return HTTPException(status_code=401, detail="Incorrect username or password")
                return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail":"Incorrect username or password"})

            user_data = users_model.UserGet(**dict(row))
            access_token = create_access_token(data={"id": user_data.user_id,"role": user_data.user_role, "first_name": user_data.first_name, "last_name": user_data.last_name})
            return {"access_token": access_token, "token_type": "bearer"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Authentication error: {e}")