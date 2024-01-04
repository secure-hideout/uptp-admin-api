from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from typing import Optional, Union
from enum import Enum
class Status(str, Enum):
    PENDING = "Pending"
    ACCEPTED = "Approved"
    REJECTED = "Rejected"

class Transaction(BaseModel):
    id: Optional[int] = None  # bigserial in PostgreSQL is generally represented as an int in Python
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    user_id: str
    amount: Optional[float] = None
    currency: Optional[str] = None
    is_deposit: Optional[bool] = None
    status: Status
    email: Optional[str]= None

    class Config:
        orm_mode = True
