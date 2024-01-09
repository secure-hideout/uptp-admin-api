from fastapi import APIRouter, HTTPException, Query, UploadFile, Depends, Body, Path

from typing import List, Union
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from fastapi import Security, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from controllers import support_controller
from models import support_model
from utils.jwt_verify import verify_token  # Import your token verification function
import models.users_model as users_model, models.user_profile_model as user_profile_model, \
    models.trade_model as trades_model, models.transactions_model as transactions_model, models.auth_model as auth_model, models.user_config as user_config
import controllers.user_controller as user_controller, controllers.user_profile_controller as user_profile_controller, \
    controllers.trades_controller as trades_controller, controllers.transactions_controller as transactions_controller, \
    controllers.auth_controller as auth_controller, controllers.user_config as user_config_controller
router = APIRouter()

security = HTTPBearer()
async def validate_token(http_auth: HTTPAuthorizationCredentials = Security(security)):
    token = http_auth.credentials
    payload = verify_token(token)  # Replace 'YourSecretKey' with your actual secret key
    if payload is None:
        raise HTTPException(status_code=403, detail="Invalid token or expired token")
    return payload

@router.post("/create-user-config")
async def create_user_config_endpoint(request: user_config.CreateUserConfigRequest, token: str = Depends(validate_token)):
    return await user_config_controller.create_user_config(request)

@router.get("/user-config/{user_id}", response_model=user_config.UserConfigResponse)
async def get_user_config_endpoint(user_id: str, token: str = Depends(validate_token)):
    return await user_config_controller.get_user_config(user_id)

@router.put("/upsert-user-config")
async def upsert_user_config_endpoint(request: user_config.UserConfigRequest, token: str = Depends(validate_token)):
    return await user_config_controller.upsert_user_config(request)