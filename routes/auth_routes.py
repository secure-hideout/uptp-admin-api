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

@router.post("/login")
async def login(form_data: auth_model.LoginRequest):
    return await auth_controller.login_for_access_token(form_data)

@router.post("/forgot-password")
async def forgot_password_endpoint(request: users_model.ForgotPasswordRequest):
    return await user_controller.forgot_password(request)

@router.post("/update-password-userid")
async def update_password_endpoint_userid(request: users_model.UpdatePasswordRequest):
    return await user_controller.update_password_userid(request)

@router.post("/update-password")
async def update_password_endpoint(request: users_model.UpdatePasswordRequest, token: str = Depends(validate_token)):
    return await user_controller.update_password(request)

@router.post("/send-otp")
async def send_otp(email: str, token: str = Depends(validate_token)):
    otp = generate_otp()
    otp_storage[email] = otp
    await send_otp_email(email, otp)
    return {"message": "OTP sent to email"}

@router.post("/verify-otp")
async def verify_otp(email: str, otp: str, token: str = Depends(validate_token)):
    if email in otp_storage and otp_storage[email] == otp:
        del otp_storage[email]  # Remove the OTP after successful verification
        return {"message": "OTP verified successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP")
