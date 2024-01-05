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

@router.post("/send-otp")
async def send_otp(email: str, token: str = Depends(validate_token)):
    otp = generate_otp()
    otp_storage[email] = otp
    await send_otp_email(email, otp)
    return {"message": "OTP sent to email"}
@router.post("/update-password-userid")
async def update_password_endpoint_userid(request: users_model.UpdatePasswordRequestUserId):
    return await user_controller.update_password_userid(request)

@router.post("/verify-otp")
async def verify_otp(email: str, otp: str, token: str = Depends(validate_token)):
    if email in otp_storage and otp_storage[email] == otp:
        del otp_storage[email]  # Remove the OTP after successful verification
        return {"message": "OTP verified successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP")

@router.post("/login")
async def login(form_data: auth_model.LoginRequest):
    return await auth_controller.login_for_access_token(form_data)

@router.post("/forgot-password")
async def forgot_password_endpoint(request: users_model.ForgotPasswordRequest):
    return await user_controller.forgot_password(request)

@router.get("/users", response_model=List[users_model.UserGet])
async def getAll(user_id: str = Query(None), token: str = Depends(validate_token)):
    return await user_controller.read_users_by_oversee_user(user_id)


@router.get("/users/by", response_model=List[users_model.UserGet])
async def get_users_by_filter(user_role: str = Query(None), is_active: str = Query(None),
                              token: str = Depends(validate_token)):
    try:
        return await user_controller.fetch_users_by_filter(user_role, is_active)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/user", response_model=users_model.UserGet)
async def create_user(user_data: users_model.User):
    return await user_controller.create_user(user_data)


@router.patch("/user", response_model=users_model.UserGet)
async def update_user_endpoint(update_data: users_model.UserUpdateModel, token: str = Depends(validate_token)):
    return await user_controller.update_user(update_data)


@router.delete("/user/{user_id}", response_model=users_model.UserGet)
async def api_delete_user(user_id: str, token: str = Depends(validate_token)):
    print(user_id)
    delete_data = users_model.UserDeleteModel(user_id=user_id)
    return await user_controller.delete_user(delete_data)


@router.post("/user/applyBalance")
async def api_apply_balance(update_data: user_profile_model.UserBalanceUpdateModel = Body(...)):
    return await user_profile_controller.update_user_balance(update_data)


@router.get("/users/getCountsByUserStatus")
async def api_get_user_counts(user_id: str = Query(None), token: str = Depends(validate_token)):
    return await user_controller.api_get_user_counts(user_id)


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

@router.post("/update-password")
async def update_password_endpoint(request: users_model.UpdatePasswordRequest):
    return await user_controller.update_password(request)
