from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from typing import Optional, Union
class Transaction(BaseModel):
    id: Union[int, None] = None # bigserial in PostgreSQL is generally represented as an int in Python
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None
    deleted_at: Union[datetime, None] = None
    user_id: str
    amount: Union[Decimal, None] = None
    currency: Union[str, None] = None
    is_deposit: Union[bool, None] = None

    class Config:
        orm_mode = True
