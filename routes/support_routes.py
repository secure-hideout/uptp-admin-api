from fastapi import APIRouter, HTTPException, Query, UploadFile, Depends, Body, Path

from typing import List, Union
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from fastapi import Security, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from controllers import support_controller
from models import support_model
from utils.jwt_verify import verify_token  # Import your token verification function
import random
import string
from utils import send_mail
# Initialize HTTPBearer
security = HTTPBearer()
router = APIRouter()

otp_storage = {}

async def validate_token(http_auth: HTTPAuthorizationCredentials = Security(security)):
    token = http_auth.credentials
    payload = verify_token(token)  # Replace 'YourSecretKey' with your actual secret key
    if payload is None:
        raise HTTPException(status_code=403, detail="Invalid token or expired token")
    return payload

@router.post("/create-ticket")
async def create_ticket(ticket_data: support_model.SupportModel):
    return await support_controller.create_ticket(ticket_data)

@router.patch("/update-ticket/{ticket_id}", response_model=support_model.SupportModel)
async def update_ticket(
    ticket_id: int,
    ticket_update: support_model.TicketUpdateModel,
     token: str = Depends(validate_token)
):

    return await support_controller.update_ticket(ticket_id, ticket_update)

@router.get("/getall-tickets", response_model=List[support_model.SupportModel])
async def get_all_tickets(token: str = Depends(validate_token)):
    return await support_controller.get_all_tickets()

@router.get("/tickets/status-counts", response_model=dict[str, int])
async def get_ticket_status_counts(token: str = Depends(validate_token)):
    return await support_controller.get_ticket_status_counts()

@router.get("/tickets/by-user/{user_id}", response_model=List[support_model.SupportModel])
async def get_tickets_by_user(user_id: str):
    return await support_controller.get_tickets_by_user(user_id)