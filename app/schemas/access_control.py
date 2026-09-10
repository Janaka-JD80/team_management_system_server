from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from uuid import UUID

class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    permission_id: UUID
    permission_name: str
    permission_description: Optional[str] = None

class RoleBase(BaseModel):
    role_name: str
    role_description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    model_config = ConfigDict(from_attributes=True)
    role_id: UUID

class RoleWithPermissionsResponse(RoleResponse):
    permissions: List[PermissionResponse] = []

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: UUID
    user_email: str
    full_name: Optional[str] = None
    is_active: bool

class UserWithRolesResponse(UserResponse):
    roles: List[RoleResponse] = []
