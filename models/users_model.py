from pydantic import BaseModel, EmailStr
from typing import Optional, Union
from datetime import datetime
from decimal import Decimal

class ForgotPasswordRequest(BaseModel):
    email: EmailStr
class User(BaseModel):
    user_id: Union[str, None] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None
    deleted_at: Union[datetime, None] = None
    email: EmailStr
    password: Union[str, None] = None
    user_role: str
    first_name: str
    last_name: str
    is_active: Union[str, None] = None  # New field
    oversee_user: str

class UserGet(BaseModel):
    user_id: Union[str, None] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None
    deleted_at: Union[datetime, None] = None
    email: Union[str, None] = None
    password: Union[str, None] = None
    user_role: Union[str, None] = None
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    is_active: Union[str, None] = None  # New field
    balance: Union[Decimal, None] = None

    @staticmethod
    def to_str(value: Decimal) -> str:
        return str(value) if value is not None else None

    @classmethod
    def from_orm(cls, obj):
        # Convert Decimal to string for the balance field
        obj_dict = obj.__dict__
        obj_dict['balance'] = cls.to_str(obj_dict.get('balance'))
        return cls(**obj_dict)

class UserUpdateModel(BaseModel):
    user_id: str
    email: Union[EmailStr, None] = None
    user_role: Union[str, None] = None
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    is_active: Union[str, None] = None  # New field

class UserDeleteModel(BaseModel):
    user_id: str
    deleted_at: Union[datetime, None] = None

    class Config:
        orm_mode = True

class UserProfile(BaseModel):
    user_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    user_type: Optional[str] = None
    is_enabled: Optional[bool] = None
    balance: Optional[float] = None  # Assuming numeric is used as float
    last_login: Optional[datetime] = None
    password_updated_at: Optional[datetime] = None
    currency: Optional[str] = None  # Corrected the field name
    time_zone: Optional[str] = None

    class Config:
        orm_mode = True

class UpdatePasswordRequest(BaseModel):
    email: EmailStr
    current_password: str
    new_password: str