from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from typing import Optional, Union

class LoginTracker(BaseModel):
    id: Union[int, None] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None
    deleted_at: Union[datetime, None] = None
    email: Union[str, None] = None
    user_id: Union[str, None] = None
    host: Union[str, None] = None
    status: Union[str, None] = None

    class Config:
        orm_mode = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
