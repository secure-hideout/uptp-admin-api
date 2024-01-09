from pydantic import BaseModel
from typing import Optional
class UsersConfig(BaseModel):
    user_id: str
    type: str
    conf: str
    value: str

    class Config:
        orm_mode = True


from pydantic import BaseModel, EmailStr
from typing import Dict, Optional

class ConfigItem(BaseModel):
    squareoff: Optional[str]
    brokerage: Optional[str]
    leverage: Optional[str]

class CreateUserConfigRequest(BaseModel):
    user_id: str
    first_name: str
    last_name: str
    email: EmailStr
    user_role: str
    config: Dict[str, ConfigItem]

class UserConfigResponse(BaseModel):
    user_id: str
    config: Dict[str, ConfigItem]

class UserConfigRequest(BaseModel):
    user_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    user_role: Optional[str] = None
    config: Dict[str, ConfigItem]