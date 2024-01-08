from fastapi import APIRouter, HTTPException, Query, UploadFile, Depends, Body, Path
import models.users_model as users_model, models.user_profile_model as user_profile_model, \
    models.trade_model as trades_model, models.transactions_model as transactions_model, models.auth_model as auth_model
import controllers.user_controller as user_controller, controllers.user_profile_controller as user_profile_controller, \
    controllers.trades_controller as trades_controller, controllers.transactions_controller as transactions_controller, \
    controllers.auth_controller as auth_controller
from typing import List, Union
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from fastapi import Security, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

@router.get("/transactions/status-count")
async def get_status_counts(token: str = Depends(validate_token)):
    try:
        return await transactions_controller.get_status_counts()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
async def send_otp_email(email: str, otp: str):
    send_mail.send_email(
        subject="OTP UPTP",
        password=otp,
        email=email,
        to_email=email,
        from_email="connect@uptp.com",
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        smtp_user="hideoutprotocol@gmail.com",
        smtp_password="bdbp opkn heyw ypaa",
        template_name="onetimeOTP.html",
    )

@router.get("/transactions/{user_id}")
async def get_transactions_by_user_id(user_id: str, token: str = Depends(validate_token)):
    try:
        return await transactions_controller.fetch_transactions_by_user_id(user_id)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/getCountsByAgentStatus")
async def api_get_agent_counts(token: str = Depends(validate_token)):
    return await user_controller.api_get_agent_counts()


@router.get("/trades/{user_id}", response_model=List[trades_model.Trade])
async def get_trades_by_user_id(user_id: str, token: str = Depends(validate_token)):
    try:
        return await trades_controller.fetch_trades_by_user_id(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alltransactions/{oversee_id}", response_model=List[transactions_model.Transaction])
async def get_transactions(oversee_id: str, status: str, token: str = Depends(validate_token)):
    try:
        return await transactions_controller.fetch_transactions(oversee_id, status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/transactions/update_status/{transaction_id}")
async def update_transaction_status(transaction_id: int, status: str, token: str = Depends(validate_token)):
    updated_transaction = await transactions_controller.update_transaction_status(transaction_id, status)
    return updated_transaction

@router.get("/user/auth/logs/{user_id}", response_model=List[auth_model.LoginTracker])
async def get_login_trackers(
        user_id: str = Path(...),
        start_date: Union[datetime, None] = Query(None),
        end_date: Union[datetime, None] = Query(None),
        token: str = Depends(validate_token)
):
    return await auth_controller.get_login_trackers_by_user_and_date(user_id, start_date, end_date)


@router.get("/agent-token-mapping/{user_id}", response_model=List[user_profile_model.AgentTokenMapping])
async def fetch_agent_token_mappings(user_id: str = Path(...), token: str = Depends(validate_token)):
    return await user_profile_controller.get_agent_token_mappings_by_user_id(user_id)


@router.post("/agent-token-mapping")
async def add_agent_token_mapping(mapping_data: user_profile_model.AgentTokenMappingPayload):
    return await user_profile_controller.create_agent_token_mapping(mapping_data)


@router.get("/zinstruments", response_model=List[trades_model.ZInstrument])
async def fetch_all_zinstruments(token: str = Depends(validate_token)):
    return await trades_controller.get_all_zinstruments()
