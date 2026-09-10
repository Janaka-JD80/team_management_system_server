from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.schemas.auth import UserCreate, UserLogin, JwtPayload
from app.models.user import User
from app.models.role import Role
from app.repositories.user_repository import user_repository
from app.repositories.role_repository import role_repository
from app.core.security import get_password_hash, verify_password, create_access_token

class AuthService:
    def _generate_auth_response(self, user: User, role_names: list, permissions: list) -> Tuple[str, JwtPayload]:
        access_token = create_access_token(
            subject=str(user.user_id), 
            user_email=user.user_email,
            full_name=user.full_name,
            roles=role_names,
            permissions=permissions
        )

        payload = JwtPayload(
            sub=str(user.user_id), 
            exp=0, 
            user_email=user.user_email,
            full_name=user.full_name,
            roles=role_names,
            permissions=permissions
        )

        return access_token, payload

    async def signup_user(self, db: AsyncSession, user_in: UserCreate) -> Tuple[str, JwtPayload]:
        # Check if email is registered
        existing_user = await user_repository.get_user_by_email(db, email=user_in.user_email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user
        hashed_password = get_password_hash(user_in.password)
        new_user = User(
            user_email=user_in.user_email,
            hashed_password=hashed_password,
            full_name=user_in.full_name
        )

        # Assign default role TEAM_MEMBER
        default_role = await role_repository.get_role_by_name(db, name="TEAM_MEMBER")
        if default_role:
            new_user.roles.append(default_role)

        new_user = await user_repository.create_user(db, new_user)
        
        role_names = ["TEAM_MEMBER"] if default_role else []
        permissions = []

        return self._generate_auth_response(new_user, role_names, permissions)

    async def authenticate_user(self, db: AsyncSession, credentials: UserLogin) -> Tuple[str, JwtPayload]:
        user = await user_repository.get_user_by_email(db, email=credentials.user_email)
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Reload user with roles using the repository
        user = await user_repository.get_users_with_roles(db, search=credentials.user_email)
        user = user[0] if user else None
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        role_names = [role.role_name for role in user.roles]
        permissions = []
        # In a full implementation, you would load permissions from the roles.
        
        return self._generate_auth_response(user, role_names, permissions)

auth_service = AuthService()
