from pydantic import BaseModel, EmailStr
from typing import Optional, Union, List
from datetime import datetime
class UserProfile(BaseModel):
    user_id: str
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None
    deleted_at: Union[datetime, None] = None
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    user_type: Union[str, None] = None
    is_enabled: Union[bool, None] = None
    balance: Union[float, None] = None
    last_login: Union[datetime, None] = None
    password_updated_at: Union[datetime, None] = None
    currency: Union[str, None] = None  # Corrected the field name
    time_zone: Union[str, None] = None

    class Config:
        orm_mode = True

class UserBalanceUpdateModel(BaseModel):
    user_id: str
    balance: float
    currency: str
    oversee_id: str

class AgentTokenMapping(BaseModel):
    user_id: str
    financial_instrument_id: int
    instrument_type: str
    tradingsymbol: Union[str, None] = None

class StockItem(BaseModel):
    id: int
    name: str
    instrument_type: str

class AgentTokenMappingPayload(BaseModel):
    user_id: str
    stocks: List[StockItem]

