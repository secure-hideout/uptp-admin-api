from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from typing import Optional, Union
from enum import Enum
class Status(str, Enum):
    PENDING = "Pending"
    ASSIGNED = "Assigned"
    Closed = "Closed"
class SupportModel(BaseModel):
    ticket_id: Optional[int] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None
    user_id: str
    agent_id: Optional[str] = None
    subject: str
    description: Optional[str] = None
    status: Status

class TicketUpdateModel(BaseModel):
    agent_id: Optional[str]=None
    status: Optional[Status]=None
