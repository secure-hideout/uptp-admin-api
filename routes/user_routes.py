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

@router.post("/user/applyBalance")
async def api_apply_balance(update_data: user_profile_model.UserBalanceUpdateModel = Body(...)):
    return await user_profile_controller.update_user_balance(update_data)

@router.patch("/user")
async def update_user_endpoint(update_data: users_model.UserUpdateModel, token: str = Depends(validate_token)):
    return await user_controller.update_user(update_data)

@router.delete("/user/{user_id}", response_model=users_model.UserGet)
async def api_delete_user(user_id: str, token: str = Depends(validate_token)):
    print(user_id)
    delete_data = users_model.UserDeleteModel(user_id=user_id)
    return await user_controller.delete_user(delete_data)

@router.get("/users/getCountsByUserStatus")
async def api_get_user_counts(user_id: str = Query(None), token: str = Depends(validate_token)):
    return await user_controller.api_get_user_counts(user_id)