from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from typing import Optional, Union
class Trade(BaseModel):
    id: Union[int, None] = None
    created_at: Union[datetime, None] = None
    updated_at: Union[datetime, None] = None
    deleted_at: Union[datetime, None] = None
    user_id: str
    financial_instrument_id: int
    instrument_type: str
    price: Decimal
    quantity: int
    buy: bool
    charges: Decimal
    total: Decimal
    currency: Union[str, None] = None
    timestamp: Union[datetime, None] = None

    class Config:
        orm_mode = True

class ZInstrument(BaseModel):
    instrument_token: int
    exchange_token: Union[int, None] = None
    tradingsymbol: Union[str, None] = None
    name: Union[str, None] = None
    last_price: Union[Decimal, None] = None
    expiry: Union[datetime, None] = None
    strike_price: Union[Decimal, None] = None
    tick_size: Union[Decimal, None] = None
    lot_size: Union[Decimal, None] = None
    instrument_type: Union[str, None] = None
    segment: Union[str, None] = None
    exchange: Union[str, None] = None
    zid: int
